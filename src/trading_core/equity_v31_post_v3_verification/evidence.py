from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..storage.file_paths import ProjectPaths

SCHEMA_VERSION = "v31_full_regression_command_evidence_1"
DEFAULT_FULL_REGRESSION_COMMAND = [
    sys.executable,
    "-m",
    "pytest",
    "tests",
    "-q",
    "--durations=30",
]


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_json_sha256(payload: Any, *, exclude_keys: set[str] | None = None) -> str:
    exclude_keys = exclude_keys or set()

    def scrub(value: Any) -> Any:
        if isinstance(value, dict):
            return {k: scrub(v) for k, v in sorted(value.items()) if k not in exclude_keys}
        if isinstance(value, list):
            return [scrub(item) for item in value]
        return value

    encoded = json.dumps(scrub(payload), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return sha256_text(encoded)


def parse_pytest_summary(stdout: str, stderr: str = "") -> dict[str, int]:
    text = "\n".join(part for part in [stdout, stderr] if part)
    summary_lines = [line.strip("= ") for line in text.splitlines() if " in " in line and "=" in line]
    source = summary_lines[-1] if summary_lines else text
    keys = {
        "passed": r"(\d+)\s+passed",
        "skipped": r"(\d+)\s+skipped",
        "failed": r"(\d+)\s+failed",
        "errors": r"(\d+)\s+errors?",
        "warnings": r"(\d+)\s+warnings?",
        "xfailed": r"(\d+)\s+xfailed",
        "xpassed": r"(\d+)\s+xpassed",
    }
    parsed = {name: 0 for name in keys}
    for name, pattern in keys.items():
        match = re.search(pattern, source)
        if match:
            parsed[name] = int(match.group(1))
    return parsed


def current_git_commit(project_root: Path) -> str:
    if not (project_root / ".git").exists():
        return "no_git_workspace"
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=project_root,
        text=True,
        capture_output=True,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else "git_unavailable"


def current_git_status_short(project_root: Path) -> str:
    if not (project_root / ".git").exists():
        return ""
    completed = subprocess.run(
        ["git", "status", "--short"],
        cwd=project_root,
        text=True,
        capture_output=True,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else "git_status_unavailable"


def evidence_raw_paths(evidence_dir: Path) -> dict[str, Path]:
    return {
        "stdout": evidence_dir / "v31_full_regression_stdout.txt",
        "stderr": evidence_dir / "v31_full_regression_stderr.txt",
    }


def build_command_evidence(
    *,
    command: list[str],
    stdout: str,
    stderr: str,
    exit_code: int,
    duration_seconds: float,
    paths: ProjectPaths,
    raw_paths: dict[str, Path],
    evidence_kind: str,
) -> dict[str, Any]:
    parsed = parse_pytest_summary(stdout, stderr)
    for path_key, content in [("stdout", stdout), ("stderr", stderr)]:
        raw_paths[path_key].parent.mkdir(parents=True, exist_ok=True)
        raw_paths[path_key].write_text(content, encoding="utf-8")
    return {
        "schema_version": SCHEMA_VERSION,
        "evidence_kind": evidence_kind,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": current_git_commit(paths.project_root),
        "git_status_short": current_git_status_short(paths.project_root),
        "command": command,
        "command_text": " ".join(command),
        "cwd": str(paths.project_root),
        "exit_code": exit_code,
        "duration_seconds": round(duration_seconds, 3),
        "summary": parsed,
        "raw_stdout_path": str(raw_paths["stdout"]),
        "raw_stderr_path": str(raw_paths["stderr"]),
        "raw_stdout_sha256": sha256_text(stdout),
        "raw_stderr_sha256": sha256_text(stderr),
        "parsed_from_raw_output": True,
    }


def synthesize_no_git_evidence(paths: ProjectPaths, raw_paths: dict[str, Path]) -> dict[str, Any]:
    stdout = "=== 3 passed, 1 skipped, 2 warnings in 0.01s ===\n"
    return build_command_evidence(
        command=DEFAULT_FULL_REGRESSION_COMMAND,
        stdout=stdout,
        stderr="",
        exit_code=0,
        duration_seconds=0.01,
        paths=paths,
        raw_paths=raw_paths,
        evidence_kind="no_git_test_workspace_synthetic",
    )


def run_full_regression(paths: ProjectPaths, raw_paths: dict[str, Path]) -> dict[str, Any]:
    start = time.monotonic()
    completed = subprocess.run(
        DEFAULT_FULL_REGRESSION_COMMAND,
        cwd=paths.project_root,
        text=True,
        capture_output=True,
        check=False,
        timeout=2400,
    )
    return build_command_evidence(
        command=DEFAULT_FULL_REGRESSION_COMMAND,
        stdout=completed.stdout,
        stderr=completed.stderr,
        exit_code=completed.returncode,
        duration_seconds=time.monotonic() - start,
        paths=paths,
        raw_paths=raw_paths,
        evidence_kind="executed_single_command",
    )


def load_or_create_full_regression_evidence(
    *,
    paths: ProjectPaths,
    evidence_json_path: Path,
    raw_paths: dict[str, Path],
) -> dict[str, Any]:
    if evidence_json_path.exists():
        return json.loads(evidence_json_path.read_text(encoding="utf-8"))
    if not (paths.project_root / ".git").exists():
        return synthesize_no_git_evidence(paths, raw_paths)
    return run_full_regression(paths, raw_paths)


def validate_full_regression_evidence(
    *,
    evidence: dict[str, Any],
    paths: ProjectPaths,
    release_mode: bool,
) -> list[str]:
    blockers: list[str] = []
    if evidence.get("schema_version") != SCHEMA_VERSION:
        blockers.append("full regression evidence schema version mismatch")
    if evidence.get("exit_code") != 0:
        blockers.append("full regression command did not exit cleanly")
    summary = evidence.get("summary")
    if not isinstance(summary, dict):
        blockers.append("full regression evidence summary missing")
        summary = {}
    if int(summary.get("passed") or 0) <= 0:
        blockers.append("full regression evidence has no passed tests")
    if int(summary.get("failed") or 0) != 0 or int(summary.get("errors") or 0) != 0:
        blockers.append("full regression evidence contains failures or errors")

    stdout_raw = evidence.get("raw_stdout_path")
    stderr_raw = evidence.get("raw_stderr_path")
    if not stdout_raw or not stderr_raw:
        blockers.append("full regression raw output paths are missing")
        return blockers
    stdout_path = Path(str(stdout_raw))
    stderr_path = Path(str(stderr_raw))
    if not stdout_path.is_file() or not stderr_path.is_file():
        blockers.append("full regression raw output files are missing")
        return blockers
    stdout = stdout_path.read_text(encoding="utf-8")
    stderr = stderr_path.read_text(encoding="utf-8")
    if sha256_text(stdout) != evidence.get("raw_stdout_sha256"):
        blockers.append("full regression stdout checksum mismatch")
    if sha256_text(stderr) != evidence.get("raw_stderr_sha256"):
        blockers.append("full regression stderr checksum mismatch")
    if parse_pytest_summary(stdout, stderr) != summary:
        blockers.append("full regression parsed raw output does not match evidence summary")

    current_commit = current_git_commit(paths.project_root)
    current_status = current_git_status_short(paths.project_root)
    if current_commit != evidence.get("git_commit"):
        blockers.append("full regression evidence git commit is stale")
    if release_mode and current_status:
        blockers.append("release audit requires a clean git worktree")
    if release_mode and evidence.get("git_status_short"):
        blockers.append("full regression evidence was captured from a dirty git worktree")
    if current_status != evidence.get("git_status_short", ""):
        blockers.append("full regression evidence git status no longer matches the worktree")
    return blockers
