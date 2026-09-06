"""Build official v1.0.0 release closeout artifacts."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import read_json, sha256_file, utc_now, write_json
from trading_core.equity_data_quality.common import BOUNDARY_FALSE, BOUNDARY_TRUE
from trading_core.storage.file_paths import ProjectPaths, project_paths

TARGET_VERSION = "v1.0.0-a-share-autonomous-simulation-platform-release"
SOURCE_VERSION = "v1.0.0-prep-a-share-autonomous-simulation-platform-closeout"
RECOMMENDED_NEXT_VERSION = "v1.0.1-a-share-benchmark-data-and-performance-claim-hardening"
DEFAULT_AS_OF_DATE = "2026-07-01"
SOURCE_READINESS_SCORE = 54
MINIMUM_OWNER_READINESS_SCORE = 75
SCORE_GAP = 21
FULL_REGRESSION_RESULT = "1807 passed, 1 skipped, 0 failed"

JSON_NAMES = [
    "v100_release_request",
    "v100_prep_verification",
    "v100_final_release_decision",
    "v100_release_scope_statement",
    "v100_safety_boundary_statement",
    "v100_known_limitations_register",
    "v100_release_manifest",
]
MARKDOWN_NAMES = [
    "A_SHARE_V100_RELEASE_SUMMARY.md",
    "A_SHARE_V100_SAFETY_AND_LIMITATIONS.md",
]
KNOWN_LIMITATIONS = [
    "owner-readiness remains blocked: 54 / 75 / gap 21",
    "not live trading ready",
    "no real broker / real account / real order support",
    "benchmark/index attribution source missing or incomplete",
    "benchmark warning blocks real performance claims",
    "autonomous LLM/RL functions are simulation-only",
    "simulated orders/fills are not real orders/fills",
    "owner must not copy simulated actions into real account",
]


def build_a_share_v100_release(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths or project_paths()
    _ensure_dirs(paths, as_of_date)
    prep = _prep_verification(paths, as_of_date)
    request = _release_request(as_of_date)
    scope = _scope_statement(as_of_date)
    safety = _safety_boundary_statement(as_of_date)
    limitations = _known_limitations_register(as_of_date)
    decision = _final_release_decision(as_of_date, prep)
    artifacts = _artifact_paths(paths, as_of_date)
    payloads = {
        "v100_release_request": request,
        "v100_prep_verification": prep,
        "v100_final_release_decision": decision,
        "v100_release_scope_statement": scope,
        "v100_safety_boundary_statement": safety,
        "v100_known_limitations_register": limitations,
    }
    for key, payload in payloads.items():
        write_json(artifacts[key], payload)
    _write_reports(artifacts, decision, limitations, safety, prep)
    manifest = _manifest(paths, as_of_date, decision)
    write_json(artifacts["v100_release_manifest"], manifest)
    return _summary(decision, prep, limitations)


def _release_request(as_of_date: str) -> dict[str, Any]:
    return {
        "request_id": "A-SHARE-V100-RELEASE-REQUEST",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "scope": [
            "verify_v100_prep",
            "generate_final_release_decision",
            "generate_release_scope_statement",
            "generate_safety_boundary_statement",
            "generate_known_limitations_register",
            "generate_release_summary",
        ],
        "no_new_platform_features": True,
        "full_pytest_reused_from_v100_prep": True,
        "full_pytest_rerun": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _prep_verification(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    decision = read_json(paths.data_dir / "equity_v100_prep" / "daily" / as_of_date / "v100_release_readiness_decision.json")
    regression = read_json(paths.data_dir / "equity_v100_prep" / "daily" / as_of_date / "v100_full_regression_result.json")
    warning = read_json(paths.data_dir / "equity_v100_prep" / "daily" / as_of_date / "v098_warning_classification.json")
    prep_audit = read_json(paths.data_dir / "equity_data_quality" / "a_share_v100_prep_audit.json")
    owner_smoke = _run([sys.executable, "-m", "trading_core.cli", "owner-daily-status", "--as-of-date", as_of_date, "--format", "json"], paths.project_root)
    v09_audit_smoke = _run([sys.executable, "-m", "trading_core.cli", "audit-a-share-v09-platform", "--as-of-date", as_of_date], paths.project_root)
    version_text = (paths.project_root / "VERSION").read_text(encoding="utf-8").strip()
    cli_version = _run([sys.executable, "-m", "trading_core.cli", "--version"], paths.project_root)
    tag = _run(["git", "tag", "--list", SOURCE_VERSION], paths.project_root)
    owner_status = _parse_json(owner_smoke["stdout"])
    blocking: list[str] = []
    checks = {
        "v100_prep_tag_exists": tag["stdout"].strip() == SOURCE_VERSION,
        "version_is_v100_prep_before_update": version_text == SOURCE_VERSION,
        "cli_version_is_100": "trading-core 1.0.0" in cli_version["stdout"],
        "v100_prep_audit_passed": prep_audit.get("overall_passed") is True,
        "v100_prep_blocking_reasons_empty": prep_audit.get("blocking_reasons") == [],
        "release_readiness_decision_ready": decision.get("release_readiness_decision") == "ready_for_v100_release",
        "full_regression_passed": regression.get("full_regression_passed") is True,
        "full_regression_counts_match": regression.get("total_passed") == 1807 and regression.get("total_skipped") == 1 and regression.get("total_failed") == 0,
        "safety_boundary_sweep_passed": decision.get("safety_boundary_sweep_passed") is True,
        "artifact_integrity_passed": decision.get("artifact_integrity_passed") is True,
        "cli_surface_verified": decision.get("cli_surface_verified") is True,
        "blocking_warning_count_zero": warning.get("blocking_warning_count") == 0,
        "benchmark_warning_classified_non_blocking": bool(warning.get("benchmark_attribution_warning_non_blocking")),
        "owner_daily_status_smoke_passed": owner_smoke["returncode"] == 0 and owner_status.get("known_owner_readiness_state") == "blocked",
        "v09_platform_audit_smoke_passed": v09_audit_smoke["returncode"] == 0,
    }
    blocking.extend(key for key, value in checks.items() if not value)
    return {
        "verification_id": "A-SHARE-V100-PREP-VERIFICATION",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        **checks,
        "full_pytest_reused_from_v100_prep": True,
        "full_pytest_rerun": False,
        "full_regression_result": FULL_REGRESSION_RESULT,
        "full_regression_duration_seconds": regression.get("duration_seconds"),
        "blocking_warning_count": warning.get("blocking_warning_count"),
        "benchmark_warning_classification": "non_blocking_for_research_only_simulation_release_blocks_real_performance_claims",
        "owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "source_readiness_score": SOURCE_READINESS_SCORE,
        "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE,
        "score_gap": SCORE_GAP,
        **BOUNDARY_FALSE,
        "v100_prep_verified": not blocking,
        "blocking_reasons": blocking,
    }


def _final_release_decision(as_of_date: str, prep: dict[str, Any]) -> dict[str, Any]:
    if not prep["v100_prep_verified"]:
        decision = "not_released_prep_verification_failed"
    elif prep.get("blocking_warning_count") != 0:
        decision = "not_released_blocking_warning"
    elif not prep["safety_boundary_sweep_passed"]:
        decision = "not_released_safety_boundary_failure"
    elif not prep["artifact_integrity_passed"]:
        decision = "not_released_artifact_integrity_failure"
    else:
        decision = "released_as_research_only_simulation_platform"
    return {
        "decision_id": "A-SHARE-V100-FINAL-RELEASE-DECISION",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "v100_prep_verified": prep["v100_prep_verified"],
        "release_readiness_decision_from_prep": "ready_for_v100_release",
        "full_regression_passed": prep["full_regression_passed"],
        "full_regression_result": FULL_REGRESSION_RESULT,
        "blocking_warning_count": prep["blocking_warning_count"],
        "safety_boundary_sweep_passed": prep["safety_boundary_sweep_passed"],
        "artifact_integrity_passed": prep["artifact_integrity_passed"],
        "cli_surface_verified": prep["cli_surface_verified"],
        "final_release_decision": decision,
        "platform_scope": "research_only_simulation_only_autonomous_research_platform",
        "not_owner_readiness_pass": True,
        "not_live_trading_ready": True,
        "not_real_trading_system": True,
        "not_investment_advice": True,
        "owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "source_readiness_score": SOURCE_READINESS_SCORE,
        "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE,
        "score_gap": SCORE_GAP,
        **BOUNDARY_FALSE,
        "blocking_reasons": prep["blocking_reasons"],
        "warnings": [],
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _scope_statement(as_of_date: str) -> dict[str, Any]:
    return {
        "statement_id": "A-SHARE-V100-RELEASE-SCOPE-STATEMENT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "platform_scope": "research_only_simulation_only_autonomous_research_platform",
        "included_capabilities": [
            "autonomous research",
            "automated simulation experiments",
            "RL simulation lab",
            "virtual broker",
            "paper ledger",
            "shadow/canary simulation",
            "simulated strategy promotion",
        ],
        "excluded_capabilities": [
            "real broker connection",
            "real brokerage account read",
            "real order placement",
            "real order preview",
            "real buy/sell signals",
            "owner-readiness pass",
            "live trading readiness",
        ],
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _safety_boundary_statement(as_of_date: str) -> dict[str, Any]:
    return {
        "statement_id": "A-SHARE-V100-SAFETY-BOUNDARY-STATEMENT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "plain_language_statement": "The v1.0.0 platform is released as research-only and simulation-only. It supports autonomous research, automated experiments, RL simulation, virtual broker, paper ledger, shadow/canary simulation, and simulated strategy promotion. It does not support real broker connection, real account reading, real order placement, real order preview, or real buy/sell signals. Owner-readiness remains blocked. This release is not live trading ready.",
        "owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _known_limitations_register(as_of_date: str) -> dict[str, Any]:
    return {
        "register_id": "A-SHARE-V100-KNOWN-LIMITATIONS-REGISTER",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "limitations": [{"limitation_id": f"V100-LIMIT-{idx:02d}", "description": item, "must_not_hide": True} for idx, item in enumerate(KNOWN_LIMITATIONS, 1)],
        "known_limitations_count": len(KNOWN_LIMITATIONS),
        "benchmark_warning_blocks_real_performance_claims": True,
        "owner_must_not_copy_simulated_actions_into_real_account": True,
        **BOUNDARY_FALSE,
    }


def _manifest(paths: ProjectPaths, as_of_date: str, decision: dict[str, Any]) -> dict[str, Any]:
    artifacts = _artifact_paths(paths, as_of_date)
    return {
        "manifest_id": "A-SHARE-V100-RELEASE-MANIFEST",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "generated_at": utc_now(),
        "json_artifact_count": len(JSON_NAMES),
        "markdown_report_count": len(MARKDOWN_NAMES),
        "artifacts": {key: _rel(path, paths.project_root) for key, path in artifacts.items()},
        "artifact_hashes": {key: sha256_file(path) for key, path in artifacts.items() if path.exists()},
        "overall_passed": decision["final_release_decision"] == "released_as_research_only_simulation_platform",
        "blocking_reasons": decision["blocking_reasons"],
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _summary(decision: dict[str, Any], prep: dict[str, Any], limitations: dict[str, Any]) -> dict[str, Any]:
    return {
        "builder_id": "A-SHARE-V100-FINAL-RELEASE",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": decision["as_of_date"],
        "overall_passed": decision["final_release_decision"] == "released_as_research_only_simulation_platform",
        "final_release_decision": decision["final_release_decision"],
        "platform_scope": decision["platform_scope"],
        "blocking_reasons": decision["blocking_reasons"],
        "warnings": decision["warnings"],
        "v100_prep_verified": decision["v100_prep_verified"],
        "release_readiness_decision_from_prep": decision["release_readiness_decision_from_prep"],
        "full_regression_passed": decision["full_regression_passed"],
        "full_regression_result": decision["full_regression_result"],
        "full_pytest_reused_from_v100_prep": prep["full_pytest_reused_from_v100_prep"],
        "full_pytest_rerun": prep["full_pytest_rerun"],
        "blocking_warning_count": decision["blocking_warning_count"],
        "benchmark_warning_classification": prep["benchmark_warning_classification"],
        "safety_boundary_sweep_passed": decision["safety_boundary_sweep_passed"],
        "artifact_integrity_passed": decision["artifact_integrity_passed"],
        "cli_surface_verified": decision["cli_surface_verified"],
        "known_limitations_count": limitations["known_limitations_count"],
        "owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "source_readiness_score": SOURCE_READINESS_SCORE,
        "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE,
        "score_gap": SCORE_GAP,
        **BOUNDARY_FALSE,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _write_reports(artifacts: dict[str, Path], decision: dict[str, Any], limitations: dict[str, Any], safety: dict[str, Any], prep: dict[str, Any]) -> None:
    _write_text(
        artifacts["release_summary"],
        "\n".join(
            [
                "# A股 v1.0.0 发布摘要",
                "",
                "## 1. Release Summary",
                f"- final_release_decision: {decision['final_release_decision']}",
                f"- platform_scope: {decision['platform_scope']}",
                "",
                "## 2. What v1.0.0 Includes",
                "- 自主研究、自动化模拟实验、RL 模拟实验室、虚拟 broker、paper ledger、shadow/canary 模拟和模拟策略晋级。",
                "",
                "## 3. v1.0.0-prep Verification",
                f"- v100_prep_verified: {decision['v100_prep_verified']}",
                f"- release_readiness_decision_from_prep: {decision['release_readiness_decision_from_prep']}",
                "",
                "## 4. Full Regression Result",
                f"- full_regression_result: {decision['full_regression_result']}",
                f"- full_pytest_reused_from_v100_prep: {prep['full_pytest_reused_from_v100_prep']}",
                f"- full_pytest_rerun: {prep['full_pytest_rerun']}",
                "",
                "## 5. Platform Scope",
                "- 本版本只发布 research-only / simulation-only 平台，不是实盘交易系统。",
                "",
                "## 6. Owner-Readiness State",
                f"- owner_readiness_state: {decision['owner_readiness_state']}",
                f"- score: {decision['source_readiness_score']} / {decision['minimum_owner_readiness_score']} / gap {decision['score_gap']}",
                "",
                "## 7. Known Limitations",
                *[f"- {item['description']}" for item in limitations["limitations"]],
                "",
                "## 8. Recommended Next Version",
                f"- {decision['recommended_next_version']}",
                "",
            ]
        ),
    )
    _write_text(
        artifacts["safety_report"],
        "\n".join(
            [
                "# A股 v1.0.0 安全边界与限制",
                "",
                "## 1. Safety Boundary",
                f"- {safety['plain_language_statement']}",
                "",
                "## 2. Simulation-Only Execution",
                "- 所有订单意图、成交、账户、ledger、实验和晋级均为模拟用途。",
                "",
                "## 3. No Real Broker / No Real Account / No Real Orders",
                "- 不连接真实 broker，不读取真实账户，不下真实订单。",
                "",
                "## 4. No Buy/Sell Signals",
                "- 任何模拟动作都不是买卖信号，也不能复制到真实账户执行。",
                "",
                "## 5. Owner-Readiness Still Blocked",
                f"- owner-readiness 仍为 blocked：{SOURCE_READINESS_SCORE} / {MINIMUM_OWNER_READINESS_SCORE} / gap {SCORE_GAP}。",
                "",
                "## 6. Benchmark Warning and Performance Claim Limitation",
                "- benchmark/index attribution source 缺失或不完整，阻止真实绩效宣称。",
                "",
                "## 7. What Users Must Not Do",
                "- 不要连接 broker、读取真实账户、下单、生成订单预览、把模拟动作当作买卖建议或实盘指令。",
                "",
                "## 8. Future Hardening",
                f"- 下一步建议：{RECOMMENDED_NEXT_VERSION}",
                "",
            ]
        ),
    )


def _artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    data_dir = paths.data_dir / "equity_v100_release" / "daily" / as_of_date
    output_dir = paths.outputs_dir / "equity_v100_release" / "daily" / as_of_date
    return {
        "v100_release_request": data_dir / "v100_release_request.json",
        "v100_prep_verification": data_dir / "v100_prep_verification.json",
        "v100_final_release_decision": data_dir / "v100_final_release_decision.json",
        "v100_release_scope_statement": data_dir / "v100_release_scope_statement.json",
        "v100_safety_boundary_statement": data_dir / "v100_safety_boundary_statement.json",
        "v100_known_limitations_register": data_dir / "v100_known_limitations_register.json",
        "v100_release_manifest": data_dir / "v100_release_manifest.json",
        "release_summary": output_dir / "A_SHARE_V100_RELEASE_SUMMARY.md",
        "safety_report": output_dir / "A_SHARE_V100_SAFETY_AND_LIMITATIONS.md",
    }


def _ensure_dirs(paths: ProjectPaths, as_of_date: str) -> None:
    for path in _artifact_paths(paths, as_of_date).values():
        path.parent.mkdir(parents=True, exist_ok=True)


def _run(command: list[str], cwd: Path) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=str(cwd), text=True, capture_output=True, timeout=120, check=False)
    return {"command": command, "returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}


def _parse_json(text: str) -> dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()
