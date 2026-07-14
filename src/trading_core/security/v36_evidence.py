"""Generate real, fail-closed V36 security assessment evidence."""

from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from trading_core.security.v36_scope import collect_v36_scope_records, sha256_file
from trading_core.storage.file_paths import project_paths


SCHEMA_VERSION = 2
POLICY_VERSION = "atlas-v36-policy-2"
RAW_NAMES = {
    "secret_scan": "secret_scan.json",
    "config_governance": "config_governance.json",
    "dependency_scan": "dependency_scan.json",
    "filesystem_path_scan": "filesystem_path_scan.json",
    "network_boundary_scan": "network_boundary_scan.json",
}
PUBLIC_NETWORK_HOSTS = {
    "cdn.cboe.com",
    "datacenter-web.eastmoney.com",
    "fred.stlouisfed.org",
    "github.com",
    "push2.eastmoney.com",
    "push2delay.eastmoney.com",
    "push2his.eastmoney.com",
    "quote.eastmoney.com",
    "query1.finance.yahoo.com",
    "data.eastmoney.com",
}
CONFIG_SUFFIXES = {".json", ".toml", ".yaml", ".yml", ".ini", ".env"}
UNSAFE_CONFIG_PATTERNS = {
    "debug_enabled": re.compile(r"(?im)^\s*debug\s*[:=]\s*(?:true|1|yes)\s*$"),
    "tls_verification_disabled": re.compile(r"(?im)^\s*(?:verify_ssl|tls_verify)\s*[:=]\s*(?:false|0|no)\s*$"),
    "insecure_override_enabled": re.compile(r"(?im)^\s*allow_insecure\s*[:=]\s*(?:true|1|yes)\s*$"),
    "authentication_disabled": re.compile(r"(?im)^\s*(?:auth_disabled|disable_auth)\s*[:=]\s*(?:true|1|yes)\s*$"),
}
ALLOWED_DESTRUCTIVE_SINKS = {
    ("src/trading_core/evaluation/historical_dry_run_replay.py", "_reset_replay_dirs"):
        {".resolve()", ".relative_to(", "refusing to delete the replay root"},
}


def generate_v36_security_evidence(project_root: Path | None = None) -> dict[str, Any]:
    root = (project_root or project_paths().project_root).resolve()
    evidence_root = root / "data" / "security_evidence"
    raw_root = evidence_root / "raw"
    raw_root.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).isoformat()

    scope_records = collect_v36_scope_records(root)
    manifest_path = evidence_root / "v36_scope_manifest.json"
    _write_json(
        manifest_path,
        {
            "schema_version": 1,
            "generated_at": generated_at,
            "scope_roots": ["src", "scripts", "tests", "config", ".github"],
            "records": scope_records,
        },
    )

    raw_payloads = {
        "secret_scan": _secret_scan(root),
        "config_governance": _config_governance_scan(root, scope_records),
        "dependency_scan": _dependency_scan(root, generated_at),
        "filesystem_path_scan": _filesystem_path_scan(root),
        "network_boundary_scan": _network_boundary_scan(root),
    }
    scans: dict[str, dict[str, Any]] = {}
    for name, raw_payload in raw_payloads.items():
        raw_path = raw_root / RAW_NAMES[name]
        _write_json(raw_path, raw_payload)
        scan = {
            "status": raw_payload["status"],
            "tool": raw_payload["tool"],
            "tool_version": raw_payload["tool_version"],
            "evidence_path": raw_path.relative_to(root).as_posix(),
            "evidence_sha256": sha256_file(raw_path),
        }
        if name == "dependency_scan":
            scan.update(
                {
                    "vulnerability_db_status": raw_payload["vulnerability_db_status"],
                    "vulnerability_db_updated_at": raw_payload["vulnerability_db_checked_at"],
                }
            )
        scans[name] = scan

    commit = _run(["git", "rev-parse", "HEAD"], root)
    status = _run(["git", "status", "--porcelain=v1"], root)
    assessment = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "scope_commit": commit["stdout"].strip(),
        "scope_worktree_dirty": bool(status["stdout"].strip()),
        "scope_manifest_path": manifest_path.relative_to(root).as_posix(),
        "scope_manifest_sha256": sha256_file(manifest_path),
        "scope_file_count": len(scope_records),
        "scans": scans,
    }
    _write_json(evidence_root / "v36_security_assessment.json", assessment)
    return assessment


def _secret_scan(root: Path) -> dict[str, Any]:
    command = [
        "detect-secrets",
        "scan",
        "--all-files",
        "--disable-plugin",
        "Base64HighEntropyString",
        "--disable-plugin",
        "HexHighEntropyString",
        "--disable-plugin",
        "IPPublicDetector",
        "--exclude-files",
        r"(?:^|[\\/])(?:\.git|__pycache__|\.pytest_cache|data[\\/]security_evidence|external_research)(?:[\\/]|$)",
        ".",
    ]
    completed = _run(command, root, timeout=300)
    try:
        scanner = json.loads(completed["stdout"])
    except json.JSONDecodeError:
        scanner = {"results": {}}
    findings: list[dict[str, Any]] = []
    for filename, rows in scanner.get("results", {}).items():
        for row in rows:
            line_number = int(row.get("line_number") or 0)
            line = _read_line(root / filename, line_number)
            findings.append(
                {
                    "filename": Path(filename).as_posix(),
                    "line_number": line_number,
                    "type": row.get("type"),
                    "verified": bool(row.get("is_verified")),
                    "triage": "reference_only" if _is_reference_only_secret_line(line) else "unreviewed",
                }
            )
    unreviewed = [item for item in findings if item["triage"] != "reference_only"]
    passed = completed["returncode"] == 0 and not unreviewed
    return {
        "status": "passed" if passed else "failed",
        "tool": "detect-secrets",
        "tool_version": str(scanner.get("version") or _tool_version(["detect-secrets", "--version"], root)),
        "command": command,
        "exit_code": completed["returncode"],
        "scanned_all_first_party_files": True,
        "excluded_third_party_mirrors": ["external_research"],
        "third_party_mirror_policy": "pinned commit verification; mirrored upstream code is not imported or executed by this project",
        "entropy_plugins_disabled_reason": "repository contains many cryptographic artifact hashes; provider, private-key, token, auth and keyword detectors remain enabled",
        "finding_count": len(findings),
        "unreviewed_finding_count": len(unreviewed),
        "findings": findings,
        "stderr": completed["stderr"],
    }


def _config_governance_scan(root: Path, scope_records: list[dict[str, Any]]) -> dict[str, Any]:
    bandit_command = ["bandit", "-r", "src", "-lll", "-iii", "-f", "json", "-q"]
    completed = _run(bandit_command, root, timeout=180)
    try:
        bandit = json.loads(completed["stdout"])
    except json.JSONDecodeError:
        bandit = {"errors": ["bandit output was not JSON"], "results": []}
    config_findings: list[dict[str, str]] = []
    scanned_config_files = 0
    for record in scope_records:
        relative = record["path"]
        path = root / relative
        if path.suffix.lower() not in CONFIG_SUFFIXES:
            continue
        scanned_config_files += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        for rule, pattern in UNSAFE_CONFIG_PATTERNS.items():
            if pattern.search(text):
                config_findings.append({"path": relative, "rule": rule})
    bandit_findings = bandit.get("results", [])
    passed = completed["returncode"] == 0 and not bandit.get("errors") and not bandit_findings and not config_findings
    return {
        "status": "passed" if passed else "failed",
        "tool": "bandit+atlas-config-policy",
        "tool_version": f"{_tool_version(['bandit', '--version'], root)}+{POLICY_VERSION}",
        "command": bandit_command,
        "exit_code": completed["returncode"],
        "bandit_high_severity_high_confidence_findings": bandit_findings,
        "bandit_errors": bandit.get("errors", []),
        "scanned_config_files": scanned_config_files,
        "unsafe_config_findings": config_findings,
        "stderr": completed["stderr"],
    }


def _dependency_scan(root: Path, checked_at: str) -> dict[str, Any]:
    command = [sys.executable, "-m", "pip_audit", ".", "--format", "json", "--progress-spinner", "off", "--desc", "off"]
    completed = _run(command, root, timeout=300)
    try:
        payload = json.loads(completed["stdout"])
    except json.JSONDecodeError:
        payload = {"dependencies": [], "fixes": []}
    vulnerabilities = [
        {"package": dep.get("name"), "version": dep.get("version"), "vulnerabilities": dep.get("vulns", [])}
        for dep in payload.get("dependencies", [])
        if dep.get("vulns")
    ]
    passed = completed["returncode"] == 0 and not vulnerabilities and bool(payload.get("dependencies"))
    return {
        "status": "passed" if passed else "failed",
        "tool": "pip-audit",
        "tool_version": _tool_version([sys.executable, "-m", "pip_audit", "--version"], root),
        "command": command,
        "exit_code": completed["returncode"],
        "vulnerability_service": "PyPI advisory service",
        "vulnerability_db_status": "available" if completed["returncode"] in {0, 1} else "not_available",
        "vulnerability_db_checked_at": checked_at,
        "dependency_count": len(payload.get("dependencies", [])),
        "vulnerabilities": vulnerabilities,
        "dependencies": payload.get("dependencies", []),
        "stderr": completed["stderr"],
    }


def _filesystem_path_scan(root: Path) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    reviewed_sinks: list[dict[str, Any]] = []
    for path in _python_files(root):
        relative = path.relative_to(root).as_posix()
        source = path.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            findings.append({"path": relative, "line": exc.lineno, "rule": "python_syntax_error"})
            continue
        parents = _parent_map(tree)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and any(keyword.arg == "shell" and _is_true(keyword.value) for keyword in node.keywords):
                findings.append({"path": relative, "line": node.lineno, "rule": "subprocess_shell_true"})
            if isinstance(node, ast.Call) and _call_name(node.func) == "shutil.rmtree":
                function = _enclosing_function(node, parents)
                requirements = ALLOWED_DESTRUCTIVE_SINKS.get((relative, function))
                function_source = ast.get_source_segment(source, function_node) if (function_node := _enclosing_function_node(node, parents)) else ""
                protected = bool(requirements) and all(token in (function_source or "") for token in requirements)
                record = {"path": relative, "line": node.lineno, "function": function, "guard_verified": protected}
                reviewed_sinks.append(record)
                if not protected:
                    findings.append({**record, "rule": "unprotected_recursive_delete"})
    return {
        "status": "passed" if not findings else "failed",
        "tool": "atlas-filesystem-path-policy",
        "tool_version": POLICY_VERSION,
        "rules": ["subprocess_shell_true", "unprotected_recursive_delete", "python_syntax_error"],
        "reviewed_destructive_sinks": reviewed_sinks,
        "findings": findings,
    }


def _network_boundary_scan(root: Path) -> dict[str, Any]:
    urls: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    for path in _python_files(root):
        relative = path.relative_to(root).as_posix()
        source = path.read_text(encoding="utf-8", errors="replace")
        for match in re.finditer(r"https?://[A-Za-z0-9._:-]+", source):
            url = match.group(0)
            parsed = urlparse(url)
            host = (parsed.hostname or "").lower()
            line = source.count("\n", 0, match.start()) + 1
            record = {"path": relative, "line": line, "url": url, "host": host}
            urls.append(record)
            if parsed.scheme != "https" or host not in PUBLIC_NETWORK_HOSTS:
                findings.append({**record, "rule": "network_host_not_allowlisted"})
        if "/broker/" in f"/{relative}" or "/accounting/" in f"/{relative}":
            if re.search(r"\b(?:urlopen|requests\.|httpx\.|socket\.)", source):
                findings.append({"path": relative, "rule": "broker_or_account_network_client"})
    return {
        "status": "passed" if not findings else "failed",
        "tool": "atlas-network-boundary-policy",
        "tool_version": POLICY_VERSION,
        "allowed_hosts": sorted(PUBLIC_NETWORK_HOSTS),
        "observed_urls": urls,
        "findings": findings,
    }


def _python_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for name in ("src", "scripts"):
        base = root / name
        if base.is_dir():
            files.extend(base.rglob("*.py"))
    return sorted(files)


def _is_reference_only_secret_line(line: str) -> bool:
    stripped = line.strip().rstrip(",")
    return bool(
        re.fullmatch(r'["\']?requires_secret["\']?\s*[:=]\s*(?:True|true)', stripped)
        or re.fullmatch(r'["\']?secret_env["\']?\s*[:=]\s*["\'][A-Z][A-Z0-9_]+["\']', stripped)
        or re.fullmatch(r'["\']secret_scan["\']\s*:\s*["\']gitleaks["\']', stripped)
        or re.fullmatch(r'["\']secret_scan["\']\s*:\s*["\']secret_scan\.json["\']', stripped)
        or "detect-secrets==" in stripped
    )


def _read_line(path: Path, line_number: int) -> str:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        return lines[line_number - 1] if 0 < line_number <= len(lines) else ""
    except OSError:
        return ""


def _run(command: list[str], cwd: Path, timeout: int = 60) -> dict[str, Any]:
    try:
        completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False, timeout=timeout)
        return {"returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"returncode": 127, "stdout": "", "stderr": str(exc)}


def _tool_version(command: list[str], cwd: Path) -> str:
    result = _run(command, cwd)
    text = (result["stdout"] or result["stderr"]).strip().splitlines()
    return text[0] if result["returncode"] == 0 and text else "unavailable"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _parent_map(tree: ast.AST) -> dict[ast.AST, ast.AST]:
    return {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}


def _enclosing_function_node(node: ast.AST, parents: dict[ast.AST, ast.AST]) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
    current = parents.get(node)
    while current is not None:
        if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return current
        current = parents.get(current)
    return None


def _enclosing_function(node: ast.AST, parents: dict[ast.AST, ast.AST]) -> str:
    function = _enclosing_function_node(node, parents)
    return function.name if function else "<module>"


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _call_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""


def _is_true(node: ast.AST) -> bool:
    return isinstance(node, ast.Constant) and node.value is True


def main() -> int:
    assessment = generate_v36_security_evidence()
    passed = all(scan.get("status") == "passed" for scan in assessment["scans"].values())
    print(json.dumps({"passed": passed, "assessment_path": "data/security_evidence/v36_security_assessment.json"}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
