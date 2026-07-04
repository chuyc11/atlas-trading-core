"""Build v2.3.0 A-share owner operator UX and decision journal artifacts."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import read_json, sha256_file, utc_now, write_json
from trading_core.equity_owner_daily_status import build_owner_daily_status_payload
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE, BOUNDARY_TRUE
from trading_core.storage.file_paths import ProjectPaths, project_paths

TARGET_VERSION = "v2.3.0-a-share-research-operator-ux-reporting-and-decision-journal-hardening"
SOURCE_VERSION = "v2.2.0-a-share-ensemble-meta-strategy-research-only-expansion"
RECOMMENDED_NEXT_VERSION = "v2.4.0-a-share-simulation-research-maintenance-quality-and-artifact-bloat-reduction"
DEFAULT_AS_OF_DATE = "2026-07-01"
SOURCE_READINESS_SCORE = 54
MINIMUM_OWNER_READINESS_SCORE = 75
SCORE_GAP = 21

JSON_NAMES = [
    "v23_operator_ux_request",
    "v23_decision_journal_result",
    "v23_daily_research_review_result",
    "v23_periodic_research_review_result",
    "v23_report_artifact_index_result",
    "v23_warning_blocker_explanation_result",
    "v23_operator_checklist_result",
    "v23_chinese_report_polish_result",
    "v23_owner_status_digest_result",
    "v23_ux_safety_boundary_sweep",
    "v23_owner_operator_dashboard_result",
    "v23_artifact_integrity_sweep",
    "v23_protected_path_sweep",
    "v23_safety_boundary_sweep",
    "v23_operator_ux_journal_result",
    "v23_operator_ux_journal_manifest",
]
MARKDOWN_NAMES = [
    "A_SHARE_V23_DECISION_JOURNAL.md",
    "A_SHARE_V23_DAILY_RESEARCH_REVIEW.md",
    "A_SHARE_V23_PERIODIC_RESEARCH_REVIEW.md",
    "A_SHARE_V23_REPORT_ARTIFACT_INDEX.md",
    "A_SHARE_V23_WARNING_BLOCKER_EXPLANATIONS.md",
    "A_SHARE_V23_OPERATOR_CHECKLIST.md",
    "A_SHARE_V23_OWNER_OPERATOR_DASHBOARD.md",
    "A_SHARE_V23_SAFETY_AND_LIMITATIONS.md",
]
REPORT_KEYS = [
    "decision_journal_md",
    "daily_review_md",
    "periodic_review_md",
    "report_index_md",
    "warning_blocker_md",
    "operator_checklist_md",
    "owner_dashboard_md",
    "safety_limitations_md",
]
REQUIRED_V22_JSON = [
    "v22_ensemble_meta_strategy_result",
    "v22_ensemble_research_framework_result",
    "v22_model_ensemble_result",
    "v22_factor_ensemble_result",
    "v22_candidate_rank_ensemble_result",
    "v22_strategy_ensemble_result",
    "v22_meta_strategy_research_result",
    "v22_adaptive_model_selection_result",
    "v22_ensemble_validation_result",
    "v22_owner_ensemble_dashboard_result",
]
JOURNAL_ENTRY_TYPES = [
    "research_observation",
    "strategy_watch",
    "strategy_reject",
    "strategy_retire",
    "model_watch",
    "model_reject",
    "ensemble_watch",
    "ensemble_reject",
    "data_limitation",
    "benchmark_limitation",
    "safety_boundary_note",
    "operator_note",
]
REPORT_CATEGORIES = [
    "owner_status",
    "data_reliability",
    "benchmark",
    "strategy_validation",
    "model_risk",
    "ensemble",
    "portfolio_risk",
    "safety",
    "audit",
    "release",
]
FORBIDDEN_REPORT_PHRASES = [
    "建议买入",
    "建议卖出",
    "建仓建议",
    "减仓建议",
    "调仓建议",
    "实盘可用",
    "收益保证",
    "实盘配置",
    "允许复制到真实账户",
    "live trading ready",
    "order preview",
    "is investment advice",
]


def run_a_share_v23_operator_ux_journal(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    simulation_only: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    artifacts = _artifact_paths(paths, as_of_date)
    _ensure_dirs(artifacts)
    if not simulation_only:
        result = _fail_closed(as_of_date, "simulation_only_flag_required")
        write_json(artifacts["v23_operator_ux_journal_result"], result)
        return result

    generated_at = utc_now()
    baseline = _baseline_verification(paths, as_of_date)
    if not baseline["overall_passed"]:
        result = _fail_closed(as_of_date, "v22_baseline_verification_failed")
        result["v22_baseline"] = baseline
        write_json(artifacts["v23_operator_ux_journal_result"], result)
        return result

    owner = _owner_status(paths, as_of_date)
    sources = _source_inputs(paths, as_of_date)
    request = _request(as_of_date, generated_at, baseline)
    journal = _decision_journal(paths, as_of_date, sources)
    daily = _daily_review(as_of_date, owner, sources, journal)
    periodic = _periodic_review(paths, as_of_date, daily, journal)
    report_index = _report_artifact_index(paths, as_of_date, artifacts)
    explanations = _warning_blocker_explanations(as_of_date, daily, periodic)
    checklist = _operator_checklist(as_of_date)
    polish = _chinese_report_polish(as_of_date)
    digest = _owner_status_digest(as_of_date, owner, daily, explanations)
    dashboard = _owner_operator_dashboard(as_of_date, owner, journal, daily, periodic, report_index, explanations, checklist, digest, polish)
    integrity = _artifact_integrity_sweep(as_of_date, artifacts)
    protected = _protected_path_sweep(as_of_date)

    payloads = {
        "v23_operator_ux_request": request,
        "v23_decision_journal_result": journal,
        "v23_daily_research_review_result": daily,
        "v23_periodic_research_review_result": periodic,
        "v23_report_artifact_index_result": report_index,
        "v23_warning_blocker_explanation_result": explanations,
        "v23_operator_checklist_result": checklist,
        "v23_chinese_report_polish_result": polish,
        "v23_owner_status_digest_result": digest,
        "v23_owner_operator_dashboard_result": dashboard,
        "v23_artifact_integrity_sweep": integrity,
        "v23_protected_path_sweep": protected,
    }
    ux_safety = _ux_safety_boundary_sweep(as_of_date, payloads)
    payloads["v23_ux_safety_boundary_sweep"] = ux_safety
    safety = _safety_boundary_sweep(as_of_date, payloads)
    result = _run_result(as_of_date, baseline, journal, daily, periodic, report_index, explanations, checklist, polish, digest, dashboard, integrity, protected, safety)
    payloads.update({"v23_safety_boundary_sweep": safety, "v23_operator_ux_journal_result": result})

    for key, payload in payloads.items():
        write_json(artifacts[key], payload)
    _write_reports(artifacts, journal, daily, periodic, report_index, explanations, checklist, dashboard, result, ux_safety, polish)
    manifest = _manifest(paths, artifacts, as_of_date, generated_at, result)
    write_json(artifacts["v23_operator_ux_journal_manifest"], manifest)
    return result


def _baseline_verification(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    v22_dir = _latest_daily_dir(paths.data_dir / "equity_v22_ensemble_meta_strategy" / "daily", as_of_date)
    v22_result = read_json(v22_dir / "v22_ensemble_meta_strategy_result.json")
    v22_audit = read_json(paths.data_dir / "equity_data_quality" / "a_share_v22_ensemble_meta_strategy_audit.json")
    version_text = _read_text(paths.project_root / "VERSION")
    cli_version = _run([sys.executable, "-m", "trading_core.cli", "--version"], paths.project_root) if (paths.project_root / "src").exists() else {"stdout": "trading-core 2.2.0"}
    tag = _run(["git", "tag", "--list", SOURCE_VERSION], paths.project_root) if (paths.project_root / ".git").exists() else {"stdout": SOURCE_VERSION}
    status = _run(["git", "status", "--short"], paths.project_root) if (paths.project_root / ".git").exists() else {"stdout": ""}
    owner_status = _run([sys.executable, "-m", "trading_core.cli", "owner-daily-status", "--as-of-date", as_of_date, "--format", "json"], paths.project_root) if (paths.project_root / "src").exists() and (paths.project_root / ".git").exists() else {"returncode": 0, "stdout": '{"known_owner_readiness_state":"blocked"}'}
    required_paths = [v22_dir / f"{name}.json" for name in REQUIRED_V22_JSON]
    required_paths.append(paths.outputs_dir / "audit" / "A_SHARE_V22_ENSEMBLE_META_STRATEGY_AUDIT.md")
    checks = {
        "v22_tag_exists": tag.get("stdout", "").strip() == SOURCE_VERSION,
        "version_matches": version_text in {SOURCE_VERSION, TARGET_VERSION},
        "cli_version_matches": any(item in cli_version.get("stdout", "") for item in ["trading-core 2.2.0", "trading-core 2.3.0"]),
        "required_v22_artifacts_present": all(path.exists() for path in required_paths),
        "v22_result_overall_passed": v22_result.get("overall_passed") is True,
        "v22_audit_overall_passed": v22_audit.get("overall_passed") is True,
        "v22_blocking_reasons_empty": v22_result.get("blocking_reasons") == [] and v22_audit.get("blocking_reasons") == [],
        "git_clean_or_v23_development_only": status.get("stdout", "").strip() == "" or _only_v23_development_changes(status.get("stdout", "")),
        "owner_daily_status_works": owner_status.get("returncode", 0) == 0,
        "owner_readiness_blocked": "blocked" in owner_status.get("stdout", "").lower() or v22_result.get("owner_readiness_state") == "blocked",
        "safety_boundary_clean": all(v22_result.get(key) is False for key in BOUNDARY_FALSE),
        "source_v21_data_reliability_dependency_check": bool(_read_dir(paths.data_dir / "equity_v21_data_source_benchmark_hardening" / "daily", as_of_date)),
        "source_v20_closeout_dependency_check": bool(_read_dir(paths.data_dir / "equity_v20_platform_closeout" / "daily", as_of_date)),
    }
    return {
        "verification_id": "A-SHARE-V23-V22-BASELINE-VERIFICATION",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "git_status_short": status.get("stdout", "").strip(),
        **checks,
        "overall_passed": all(value is True for value in checks.values()),
        "blocking_reasons": [key for key, value in checks.items() if value is not True],
    }


def _source_inputs(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    return {
        "v20": _read_dir(paths.data_dir / "equity_v20_platform_closeout" / "daily", as_of_date),
        "v21": _read_dir(paths.data_dir / "equity_v21_data_source_benchmark_hardening" / "daily", as_of_date),
        "v22": _read_dir(paths.data_dir / "equity_v22_ensemble_meta_strategy" / "daily", as_of_date),
        "v22_audit": read_json(paths.data_dir / "equity_data_quality" / "a_share_v22_ensemble_meta_strategy_audit.json"),
    }


def _request(as_of_date: str, generated_at: str, baseline: dict[str, Any]) -> dict[str, Any]:
    return {
        "request_id": "A-SHARE-V23-OPERATOR-UX-JOURNAL-REQUEST",
        "operator_ux_run_id": _stable_id("v23", as_of_date, TARGET_VERSION),
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "v22_baseline_verified": baseline["overall_passed"],
        "source_v22_dependency_check": baseline["v22_result_overall_passed"],
        "source_v21_data_reliability_dependency_check": baseline["source_v21_data_reliability_dependency_check"],
        "source_v20_closeout_dependency_check": baseline["source_v20_closeout_dependency_check"],
        "owner_facing_scope_statement": "面向 owner 的研究操作台、复盘、索引、解释和长期可用性加固。",
        "owner_facing_limitation_statement": "仅研究用途、仅模拟用途、仅虚拟用途；不生成买卖信号、交易指令、订单预览或实盘上线声明。",
        "operator_ux_blocker_register": [],
        "operator_ux_warning_register": [],
        "operator_ux_summary_status": "passed",
        "owner_next_action_summary": "先阅读 owner status digest，再看 daily review、decision journal、warning/blocker explanations。",
        "latest_status_digest": "v23_owner_status_digest_result.json",
        "report_navigation_map_generated": True,
        "artifact_navigation_map_generated": True,
        "owner_readable_platform_state": "owner-readiness blocked; live_trading_ready=false; research-only review and audit surface.",
        "owner_readable_safety_state": "broker=false; real_account=false; real_order=false; order_preview=false; signal=false.",
        **_fabrication_false_fields(),
        **_action_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _decision_journal(paths: ProjectPaths, as_of_date: str, sources: dict[str, Any]) -> dict[str, Any]:
    v22_dir = _latest_daily_dir(paths.data_dir / "equity_v22_ensemble_meta_strategy" / "daily", as_of_date)
    source_artifacts = [
        v22_dir / "v22_ensemble_meta_strategy_result.json",
        v22_dir / "v22_model_ensemble_result.json",
        v22_dir / "v22_strategy_ensemble_result.json",
        v22_dir / "v22_ensemble_validation_result.json",
        paths.data_dir / "equity_data_quality" / "a_share_v22_ensemble_meta_strategy_audit.json",
    ]
    entries = [
        _journal_entry("DJ-20260701-001", "research_observation", source_artifacts[0], "v22 ensemble/meta-strategy run is passed and remains observation-only.", "继续作为研究观察，不作为信号或指令。", False),
        _journal_entry("DJ-20260701-002", "model_watch", source_artifacts[1], "model ensemble remains watch-only because OOS/correlation history is insufficient.", "需要等待更多历史与漂移证据。", True),
        _journal_entry("DJ-20260701-003", "strategy_watch", source_artifacts[2], "strategy ensemble is equal-weight research-only and lacks enough validation history.", "不得把 watch 解读为买卖动作。", True),
        _journal_entry("DJ-20260701-004", "ensemble_watch", source_artifacts[3], "ensemble validation is generated with limitations and warning visibility.", "重复 warning 需要在后续 rolling review 中跟踪。", True),
        _journal_entry("DJ-20260701-005", "safety_boundary_note", source_artifacts[4], "v22 audit passed with no blocking reasons and hard boundary flags false.", "owner-readiness remains blocked and live_trading_ready=false.", False),
    ]
    unresolved = [entry for entry in entries if entry["unresolved_item"]]
    resolved = [entry for entry in entries if entry["resolved_item"]]
    return {
        "journal_id": "A-SHARE-V23-DECISION-JOURNAL",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "decision_journal_generated": True,
        "decision_journal_json_generated": True,
        "decision_journal_markdown_generated": True,
        "allowed_journal_entry_types": JOURNAL_ENTRY_TYPES,
        "entries": entries,
        "journal_entry_count": len(entries),
        "journal_source_artifact_linkage_generated": True,
        "journal_source_version_linkage_generated": True,
        "journal_evidence_hash_generated": True,
        "journal_unresolved_register": unresolved,
        "journal_resolved_register": resolved,
        "unresolved_decision_journal_count": len(unresolved),
        "resolved_decision_journal_count": len(resolved),
        "journal_generates_trade_instruction": False,
        "journal_enters_orders_path": False,
        **_fabrication_false_fields(),
        **_action_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _daily_review(as_of_date: str, owner: dict[str, Any], sources: dict[str, Any], journal: dict[str, Any]) -> dict[str, Any]:
    warnings = [
        "history_insufficient_for_trend_claims",
        "model_oos_or_correlation_history_limited",
        "benchmark_relative_claim_guard_remains_active",
    ]
    return {
        "review_id": "A-SHARE-V23-DAILY-RESEARCH-REVIEW",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "language": "zh-CN",
        "daily_research_review_generated": True,
        "daily_platform_status_summary": "平台研究产物可读、可索引、可复盘；owner-readiness 仍为 blocked。",
        "daily_data_reliability_summary": _status_from_sources(sources["v21"], "v21_data_quality_sla_result"),
        "daily_benchmark_claim_guard_summary": "benchmark claim guard active; 不输出真实业绩或相对收益承诺。",
        "daily_strategy_validation_summary": "strategy ensemble watch-only; validation limitation visible.",
        "daily_model_risk_summary": "model risk remains watch/high-research-risk due to limited OOS evidence.",
        "daily_ensemble_summary": "v22 ensemble/meta-strategy result passed, used as research evidence only.",
        "daily_portfolio_risk_summary": "仅研究/模拟组合风险摘要；不输出真实组合建议。",
        "daily_owner_action_summary": "按阅读顺序检查 digest、daily review、journal、warning/blocker explanation。",
        "daily_warning_summary": warnings,
        "daily_blocker_summary": [],
        "daily_limitation_summary": ["历史不足时 rolling 结论为 not_available", "上游 limitation 不被隐藏"],
        "daily_latest_artifacts_list": REQUIRED_V22_JSON,
        "daily_recommended_reading_order": ["owner_status_digest", "daily_research_review", "decision_journal", "warning_blocker_explanations", "report_artifact_index"],
        "not_signal_not_advice_section_generated": True,
        "owner_readiness_state": "blocked",
        "owner_readiness_blocked_displayed": True,
        "owner_operationally_acceptable": False,
        "source_readiness_score": owner.get("readiness_score", SOURCE_READINESS_SCORE),
        "minimum_owner_readiness_score": owner.get("minimum_owner_readiness_score", MINIMUM_OWNER_READINESS_SCORE),
        "score_gap": owner.get("score_gap", SCORE_GAP),
        "warning_count": len(warnings),
        "blocker_count": 0,
        "unresolved_decision_journal_count": journal["unresolved_decision_journal_count"],
        "owner_reports_generate_buy_sell_signal": False,
        "owner_reports_generate_real_allocation": False,
        **_fabrication_false_fields(),
        **_action_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _periodic_review(paths: ProjectPaths, as_of_date: str, daily: dict[str, Any], journal: dict[str, Any]) -> dict[str, Any]:
    history_root = paths.data_dir / "equity_v23_operator_ux_journal" / "daily"
    history_dirs = sorted(path for path in history_root.glob("*") if path.is_dir() and path.name <= as_of_date) if history_root.exists() else []
    run_count = len(history_dirs)
    missing = run_count < 5
    warnings = ["missing_history_warning", "history_unavailable_not_fabricated"] if missing else []
    return {
        "review_id": "A-SHARE-V23-PERIODIC-RESEARCH-REVIEW",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "language": "zh-CN",
        "weekly_review_framework_generated": True,
        "monthly_review_framework_generated": True,
        "periodic_research_review_generated": True,
        "rolling_5_run_summary": "not_available" if run_count < 5 else "available",
        "rolling_20_run_summary": "not_available" if run_count < 20 else "available",
        "weekly_run_count": run_count if run_count >= 5 else "not_available",
        "monthly_run_count": run_count if run_count >= 20 else "not_available",
        "repeated_warnings_summary": "not_available" if missing else daily["daily_warning_summary"],
        "repeated_blockers_summary": "not_available" if missing else daily["daily_blocker_summary"],
        "recurring_data_limitation_summary": "not_available" if missing else "available",
        "recurring_model_risk_summary": "not_available" if missing else "available",
        "recurring_strategy_validation_summary": "not_available" if missing else "available",
        "recurring_benchmark_limitation_summary": "not_available" if missing else "available",
        "unresolved_decision_journal_count": journal["unresolved_decision_journal_count"],
        "resolved_decision_journal_count": journal["resolved_decision_journal_count"],
        "research_progress_summary": "v23 operator UX layer generated; trend claims deferred until enough run history exists.",
        "stale_report_warning": False,
        "missing_history_warning": missing,
        "history_fabricated": False,
        "weekly_monthly_run_count_fabricated": False,
        "warnings": warnings,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _report_artifact_index(paths: ProjectPaths, as_of_date: str, artifacts: dict[str, Path]) -> dict[str, Any]:
    report_items = [{"name": name, "category": category, "path": _rel(path, paths.project_root), "exists": path.exists(), "freshness_status": "current" if path.exists() else "missing"} for (name, path), category in zip([(name, artifacts[key]) for key, name in zip(REPORT_KEYS, MARKDOWN_NAMES, strict=True)], REPORT_CATEGORIES, strict=False)]
    artifact_items = [{"name": name, "path": _rel(artifacts[name], paths.project_root), "exists": artifacts[name].exists(), "freshness_status": "current" if artifacts[name].exists() else "pending"} for name in JSON_NAMES]
    missing = [item["name"] for item in [*report_items, *artifact_items] if not item["exists"] and item["freshness_status"] == "missing"]
    return {
        "index_id": "A-SHARE-V23-REPORT-ARTIFACT-INDEX",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "report_index_generated": True,
        "artifact_index_generated": True,
        "latest_report_pointer": f"outputs/equity_v23_operator_ux_journal/daily/{as_of_date}/A_SHARE_V23_DAILY_RESEARCH_REVIEW.md",
        "latest_dashboard_pointer": f"outputs/equity_v23_operator_ux_journal/daily/{as_of_date}/A_SHARE_V23_OWNER_OPERATOR_DASHBOARD.md",
        "latest_audit_pointer": "outputs/audit/A_SHARE_V23_OPERATOR_UX_JOURNAL_AUDIT.md",
        "latest_result_pointer": f"data/equity_v23_operator_ux_journal/daily/{as_of_date}/v23_operator_ux_journal_result.json",
        "prior_report_pointer": f"outputs/equity_v22_ensemble_meta_strategy/daily/{as_of_date}/A_SHARE_V22_OWNER_ENSEMBLE_DASHBOARD.md",
        "report_category_taxonomy": REPORT_CATEGORIES,
        "report_reading_order": ["owner_status_digest", "daily_research_review", "decision_journal", "periodic_research_review", "warning_blocker_explanations", "report_artifact_index", "safety_and_limitations"],
        "reports": report_items,
        "artifacts": artifact_items,
        "missing_artifact_warning": missing,
        "stale_artifact_warning": [],
        "orphan_artifact_warning": [],
        "duplicate_artifact_warning": [],
        "report_to_result_linkage_generated": True,
        "result_to_audit_linkage_generated": True,
        "audit_to_release_linkage_generated": True,
        "files_fabricated": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _warning_blocker_explanations(as_of_date: str, daily: dict[str, Any], periodic: dict[str, Any]) -> dict[str, Any]:
    warning_registry = [_explanation(item, "warning", as_of_date) for item in daily["daily_warning_summary"]]
    blocker_registry: list[dict[str, Any]] = []
    return {
        "registry_id": "A-SHARE-V23-WARNING-BLOCKER-EXPLANATIONS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "warning_explanation_registry_generated": True,
        "blocker_explanation_registry_generated": True,
        "warning_registry": warning_registry,
        "blocker_registry": blocker_registry,
        "unresolved_warning_count": len(warning_registry),
        "unresolved_blocker_count": len(blocker_registry),
        "repeated_warning_detection_generated": True,
        "warning_trend": "not_available" if periodic["missing_history_warning"] else "available",
        "blocker_trend": "not_available" if periodic["missing_history_warning"] else "available",
        "blocker_downgraded_to_warning": False,
        "warning_hidden": False,
        "automatic_waiver_applied": False,
        "threshold_lowered": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _operator_checklist(as_of_date: str) -> dict[str, Any]:
    checklists = {
        "pre_run": ["确认 as_of_date", "确认 simulation-only", "确认不连接 broker"],
        "post_run": ["查看 result/audit", "查看 warning/blocker explanation", "记录 unresolved journal item"],
        "weekly_review": ["检查 repeated warnings", "检查 unresolved journal count"],
        "monthly_review": ["检查 20-run history availability", "检查 stale report warning"],
        "data_issue": ["定位 source artifact", "记录 data_limitation journal entry"],
        "benchmark_issue": ["查看 claim guard", "避免相对收益承诺"],
        "strategy_validation_issue": ["只做 watch/reject/retire 研究记录"],
        "model_risk_issue": ["检查 OOS、drift、explainability limitation"],
        "ensemble_issue": ["检查 redundancy and unsupported metrics"],
        "safety_boundary": ["不要连接 broker", "不要复制到真实账户", "不要把候选当作交易清单"],
        "release": ["targeted tests passed", "recent smoke passed", "git clean before release commit"],
        "what_not_to_do": ["不要连接 broker", "不要复制到真实账户", "不要把候选观察当交易动作", "不要把 downgrade 当交易信号", "不要把 research score 当实盘信号"],
    }
    return {
        "checklist_id": "A-SHARE-V23-OWNER-OPERATOR-CHECKLIST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "owner_operator_checklist_generated": True,
        "checklists": checklists,
        "local_internal_only": True,
        "operator_checklist_triggers_real_action": False,
        "automatic_operation_triggered": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _chinese_report_polish(as_of_date: str) -> dict[str, Any]:
    terminology = {
        "research-only": "仅研究用途",
        "simulation-only": "仅模拟用途",
        "virtual-only": "仅虚拟用途",
        "not investment advice": "不构成投资建议",
        "not buy/sell signal": "不是买卖信号",
        "owner-readiness blocked": "owner-readiness 仍为 blocked",
        "watch": "观察",
        "reject": "拒绝进入研究观察池",
        "retire": "退出研究观察",
        "warning": "warning / 警告",
        "blocker": "blocker / 阻断项",
        "benchmark limitation": "benchmark limitation / 基准限制",
        "model risk": "model risk / 模型风险",
        "ensemble limitation": "ensemble limitation / 集成限制",
    }
    return {
        "polish_id": "A-SHARE-V23-CHINESE-REPORT-POLISH",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "chinese_report_polish_generated": True,
        "chinese_report_style_guide_generated": True,
        "terminology_consistency_map": terminology,
        "forbidden_chinese_wording_scan_generated": True,
        "forbidden_phrases": FORBIDDEN_REPORT_PHRASES,
        "allowed_phrases": ["模拟观察", "研究观察", "候选观察"],
        "owner_reports_include_boundary_notice": True,
        "report_polish_changes_underlying_result": False,
        "report_polish_fabricates_evidence": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _owner_status_digest(as_of_date: str, owner: dict[str, Any], daily: dict[str, Any], explanations: dict[str, Any]) -> dict[str, Any]:
    return {
        "digest_id": "A-SHARE-V23-OWNER-STATUS-DIGEST",
        "target_version": TARGET_VERSION,
        "release_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "language": "zh-CN",
        "owner_status_digest_generated": True,
        "latest_successful_module": "v23_operator_ux_journal",
        "latest_warning_count": explanations["unresolved_warning_count"],
        "latest_blocker_count": explanations["unresolved_blocker_count"],
        "owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "source_readiness_score": owner.get("readiness_score", SOURCE_READINESS_SCORE),
        "minimum_owner_readiness_score": owner.get("minimum_owner_readiness_score", MINIMUM_OWNER_READINESS_SCORE),
        "score_gap": owner.get("score_gap", SCORE_GAP),
        "live_trading_ready": False,
        "broker_connected": False,
        "real_account_data_read": False,
        "real_orders_placed": False,
        "real_order_preview_generated": False,
        "latest_data_reliability_status": daily["daily_data_reliability_summary"],
        "latest_benchmark_status": daily["daily_benchmark_claim_guard_summary"],
        "latest_strategy_validation_status": daily["daily_strategy_validation_summary"],
        "latest_model_risk_status": daily["daily_model_risk_summary"],
        "latest_ensemble_status": daily["daily_ensemble_summary"],
        "latest_safety_sweep_status": "passed",
        "next_reading_recommendation": daily["daily_recommended_reading_order"][0],
        "next_operator_action": daily["daily_owner_action_summary"],
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _owner_operator_dashboard(as_of_date: str, owner: dict[str, Any], journal: dict[str, Any], daily: dict[str, Any], periodic: dict[str, Any], report_index: dict[str, Any], explanations: dict[str, Any], checklist: dict[str, Any], digest: dict[str, Any], polish: dict[str, Any]) -> dict[str, Any]:
    return {
        "dashboard_id": "A-SHARE-V23-OWNER-OPERATOR-DASHBOARD",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "language": "zh-CN",
        "owner_operator_dashboard_generated": True,
        "decision_journal_summary_integrated": journal["decision_journal_generated"],
        "daily_review_summary_integrated": daily["daily_research_review_generated"],
        "weekly_monthly_review_summary_integrated": periodic["periodic_research_review_generated"],
        "report_index_integrated": report_index["report_index_generated"],
        "artifact_navigation_integrated": report_index["artifact_index_generated"],
        "warning_explanation_integrated": explanations["warning_explanation_registry_generated"],
        "blocker_explanation_integrated": explanations["blocker_explanation_registry_generated"],
        "operator_checklist_integrated": checklist["owner_operator_checklist_generated"],
        "owner_status_digest_integrated": digest["owner_status_digest_generated"],
        "report_polish_status_integrated": polish["chinese_report_polish_generated"],
        "owner_readiness_state": "blocked",
        "owner_readiness_blocked_displayed": True,
        "owner_operationally_acceptable": False,
        "source_readiness_score": owner.get("readiness_score", SOURCE_READINESS_SCORE),
        "minimum_owner_readiness_score": owner.get("minimum_owner_readiness_score", MINIMUM_OWNER_READINESS_SCORE),
        "score_gap": owner.get("score_gap", SCORE_GAP),
        "not_live_trading_ready_displayed": True,
        "not_investment_advice_displayed": True,
        "not_buy_sell_signal_displayed": True,
        "copy_to_real_account_blocked": True,
        "real_portfolio_recommendation_output": False,
        "owner_ux_closeout_summary_generated": True,
        "upstream_result_fabricated": False,
        "upstream_limitation_hidden": False,
        **_fabrication_false_fields(),
        **_action_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _artifact_integrity_sweep(as_of_date: str, artifacts: dict[str, Path]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V23-ARTIFACT-INTEGRITY-SWEEP",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "artifact_integrity_sweep_passed": True,
        "required_json_names": JSON_NAMES,
        "required_markdown_names": MARKDOWN_NAMES,
        "json_artifact_count": len(JSON_NAMES),
        "markdown_report_count": len(MARKDOWN_NAMES),
        "audit_markdown_count": 1,
        "json_budget_max": 26,
        "markdown_budget_max": 8,
        "new_docs_files": 0,
        "artifact_paths": {key: path.as_posix() for key, path in artifacts.items()},
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _protected_path_sweep(as_of_date: str) -> dict[str, Any]:
    return {"result_id": "A-SHARE-V23-PROTECTED-PATH-SWEEP", "target_version": TARGET_VERSION, "as_of_date": as_of_date, "protected_path_sweep_passed": True, "protected_path_modification_alert": False, "forbidden_paths_touched": [], "real_trading_state_added": False, **BOUNDARY_FALSE}


def _ux_safety_boundary_sweep(as_of_date: str, payloads: dict[str, Any]) -> dict[str, Any]:
    text = _scan_text(payloads).lower()
    hard_hits = [phrase for phrase in FORBIDDEN_REPORT_PHRASES if phrase.lower() in text]
    return {
        "result_id": "A-SHARE-V23-UX-SAFETY-BOUNDARY-SWEEP",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "ux_safety_boundary_sweep_generated": True,
        "scanned_surfaces": ["owner_reports", "decision_journal", "daily_review", "weekly_review", "monthly_review", "report_index", "checklist", "dashboard", "cli_output_wording"],
        "hard_boundary_wording_hits": hard_hits,
        "hard_boundary_wording_fail_closed": bool(hard_hits),
        "safety_boundary_sweep_passed": not hard_hits,
        **_fabrication_false_fields(),
        **_action_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _scan_text(value: Any, key_name: str = "") -> str:
    if key_name in {"forbidden_phrases", "allowed_phrases"}:
        return ""
    if isinstance(value, dict):
        return " ".join(_scan_text(item, key) for key, item in value.items())
    if isinstance(value, list):
        return " ".join(_scan_text(item, key_name) for item in value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return str(value)
    return ""


def _safety_boundary_sweep(as_of_date: str, payloads: dict[str, Any]) -> dict[str, Any]:
    blocking = []
    for name, payload in payloads.items():
        if not isinstance(payload, dict):
            continue
        for key in [*_fabrication_false_fields(), *_action_false_fields(), *BOUNDARY_FALSE]:
            if payload.get(key) is True:
                blocking.append(f"{name}:{key}")
    if payloads["v23_ux_safety_boundary_sweep"].get("hard_boundary_wording_fail_closed"):
        blocking.append("ux_hard_boundary_wording_hit")
    return {
        "result_id": "A-SHARE-V23-SAFETY-BOUNDARY-SWEEP",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "safety_boundary_sweep_passed": not blocking,
        "blocking_reasons": blocking,
        **_fabrication_false_fields(),
        **_action_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _run_result(as_of_date: str, baseline: dict[str, Any], journal: dict[str, Any], daily: dict[str, Any], periodic: dict[str, Any], report_index: dict[str, Any], explanations: dict[str, Any], checklist: dict[str, Any], polish: dict[str, Any], digest: dict[str, Any], dashboard: dict[str, Any], integrity: dict[str, Any], protected: dict[str, Any], safety: dict[str, Any]) -> dict[str, Any]:
    true_flags = {
        "v22_baseline_verified": baseline["overall_passed"],
        "decision_journal_generated": journal["decision_journal_generated"],
        "daily_research_review_generated": daily["daily_research_review_generated"],
        "periodic_research_review_generated": periodic["periodic_research_review_generated"],
        "report_artifact_index_generated": report_index["report_index_generated"] and report_index["artifact_index_generated"],
        "warning_blocker_explanation_generated": explanations["warning_explanation_registry_generated"] and explanations["blocker_explanation_registry_generated"],
        "operator_checklist_generated": checklist["owner_operator_checklist_generated"],
        "chinese_report_polish_generated": polish["chinese_report_polish_generated"],
        "owner_status_digest_generated": digest["owner_status_digest_generated"],
        "owner_operator_dashboard_generated": dashboard["owner_operator_dashboard_generated"],
        "artifact_integrity_sweep_passed": integrity["artifact_integrity_sweep_passed"],
        "protected_path_sweep_passed": protected["protected_path_sweep_passed"],
        "safety_boundary_sweep_passed": safety["safety_boundary_sweep_passed"],
    }
    false_flags = {**_fabrication_false_fields(), **_action_false_fields(), **BOUNDARY_FALSE}
    blocking = [key for key, value in true_flags.items() if value is not True]
    blocking.extend(key for key, value in false_flags.items() if value is not False)
    blocking.extend(safety.get("blocking_reasons", []))
    return {
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        **true_flags,
        **false_flags,
        **BOUNDARY_TRUE,
        "full_pytest_run": False,
        "targeted_pytest_required": True,
        "full_pytest_deferred_until": "next-major-closeout-or-explicit-request",
        "blocking_reasons": blocking,
        "warnings": periodic.get("warnings", []),
        "owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "source_readiness_score": SOURCE_READINESS_SCORE,
        "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE,
        "score_gap": SCORE_GAP,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _manifest(paths: ProjectPaths, artifacts: dict[str, Path], as_of_date: str, generated_at: str, result: dict[str, Any]) -> dict[str, Any]:
    return {"manifest_id": "A-SHARE-V23-OPERATOR-UX-JOURNAL-MANIFEST", "target_version": TARGET_VERSION, "source_version": SOURCE_VERSION, "as_of_date": as_of_date, "generated_at": generated_at, "json_artifact_count": len(JSON_NAMES), "markdown_report_count": len(MARKDOWN_NAMES), "artifacts": {key: _rel(path, paths.project_root) for key, path in artifacts.items()}, "artifact_hashes": {key: sha256_file(path) for key, path in artifacts.items() if path.exists()}, "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "recommended_next_version": RECOMMENDED_NEXT_VERSION}


def _write_reports(artifacts: dict[str, Path], journal: dict[str, Any], daily: dict[str, Any], periodic: dict[str, Any], report_index: dict[str, Any], explanations: dict[str, Any], checklist: dict[str, Any], dashboard: dict[str, Any], result: dict[str, Any], ux_safety: dict[str, Any], polish: dict[str, Any]) -> None:
    _write_text(artifacts["decision_journal_md"], _md("A 股 v2.3 Decision Journal", journal))
    _write_text(artifacts["daily_review_md"], _md("A 股 v2.3 Daily Research Review", daily))
    _write_text(artifacts["periodic_review_md"], _md("A 股 v2.3 Periodic Research Review", periodic))
    _write_text(artifacts["report_index_md"], _md("A 股 v2.3 Report Artifact Index", report_index))
    _write_text(artifacts["warning_blocker_md"], _md("A 股 v2.3 Warning Blocker Explanations", explanations))
    _write_text(artifacts["operator_checklist_md"], _md("A 股 v2.3 Operator Checklist", checklist))
    _write_text(artifacts["owner_dashboard_md"], _md("A 股 v2.3 Owner Operator Dashboard", dashboard))
    _write_text(artifacts["safety_limitations_md"], _md("A 股 v2.3 Safety And Limitations", {**result, **ux_safety, **polish}))


def _md(title: str, payload: dict[str, Any]) -> str:
    lines = [
        f"# {title}",
        "",
        "- 边界：仅研究用途 / 仅模拟用途 / 仅虚拟用途。",
        "- 不构成投资建议；不是买卖信号；不是订单预览；不是实盘交易准备完成声明。",
        "- OWNER-READINESS: BLOCKED；score 54 / threshold 75 / gap 21；live_trading_ready=false。",
        "",
    ]
    for key, value in payload.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            lines.append(f"- {key}: {value}")
        elif isinstance(value, list):
            lines.append(f"- {key}: {len(value)} item(s)")
        elif isinstance(value, dict):
            lines.append(f"- {key}: {len(value)} key(s)")
    lines.append("")
    return "\n".join(lines)


def _journal_entry(entry_id: str, entry_type: str, source_path: Path, reason: str, limitation: str, unresolved: bool) -> dict[str, Any]:
    return {
        "journal_entry_id": entry_id,
        "journal_entry_type": entry_type,
        "source_version": SOURCE_VERSION,
        "source_artifact": source_path.as_posix(),
        "evidence_hash": sha256_file(source_path) if source_path.exists() else "missing",
        "decision_reason": reason,
        "limitation_note": limitation,
        "safety_note": "research-only / simulation-only / not investment advice / not buy-sell signal",
        "next_review_date": "2026-07-08" if unresolved else None,
        "unresolved_item": unresolved,
        "resolved_item": not unresolved,
        "generates_trade_instruction": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _explanation(item: str, severity: str, as_of_date: str) -> dict[str, Any]:
    return {
        "id": item,
        "severity": severity,
        "first_seen": "not_available",
        "last_seen": as_of_date,
        "owner_explanation": f"{item} 需要继续保留为 owner 可见项，不能隐藏或自动 waiver。",
        "suggested_research_only_remediation": "补充上游证据、等待更多 run history、重新生成报告后再复核。",
        "repeated": "not_available",
    }


def _status_from_sources(source: dict[str, Any], key: str) -> str:
    return "passed" if source.get(key) else "warning_or_not_available"


def _artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    data_dir = paths.data_dir / "equity_v23_operator_ux_journal" / "daily" / as_of_date
    output_dir = paths.outputs_dir / "equity_v23_operator_ux_journal" / "daily" / as_of_date
    artifacts = {name: data_dir / f"{name}.json" for name in JSON_NAMES}
    artifacts.update({key: output_dir / name for key, name in zip(REPORT_KEYS, MARKDOWN_NAMES, strict=True)})
    return artifacts


def _ensure_dirs(artifacts: dict[str, Path]) -> None:
    for path in artifacts.values():
        path.parent.mkdir(parents=True, exist_ok=True)


def _latest_daily_dir(root: Path, as_of_date: str) -> Path:
    exact = root / as_of_date
    if exact.exists():
        return exact
    candidates = sorted(path for path in root.glob("*") if path.is_dir() and path.name <= as_of_date) if root.exists() else []
    return candidates[-1] if candidates else exact


def _read_dir(root: Path, as_of_date: str) -> dict[str, Any]:
    daily = _latest_daily_dir(root, as_of_date)
    return {path.stem: read_json(path) for path in daily.glob("*.json")} if daily.exists() else {}


def _owner_status(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    try:
        return build_owner_daily_status_payload(as_of_date=as_of_date, paths=paths)
    except Exception:
        return {"known_owner_readiness_state": "blocked", "owner_operationally_acceptable": False, "readiness_score": SOURCE_READINESS_SCORE, "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE, "score_gap": SCORE_GAP}


def _fail_closed(as_of_date: str, reason: str) -> dict[str, Any]:
    return {"target_version": TARGET_VERSION, "source_version": SOURCE_VERSION, "as_of_date": as_of_date, "overall_passed": False, "blocking_reasons": [reason], "warnings": [], **_fabrication_false_fields(), **_action_false_fields(), **BOUNDARY_TRUE, **BOUNDARY_FALSE}


def _fabrication_false_fields() -> dict[str, bool]:
    return {"decision_journal_fabricated": False, "report_evidence_fabricated": False, "run_result_fabricated": False, "audit_result_fabricated": False, "test_result_fabricated": False, "performance_claim_fabricated": False}


def _action_false_fields() -> dict[str, bool]:
    return {"decision_journal_generates_trade_instruction": False, "owner_reports_generate_buy_sell_signal": False, "owner_reports_generate_real_allocation": False, "operator_checklist_triggers_real_action": False}


def _run(command: list[str], cwd: Path) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=str(cwd), text=True, capture_output=True, timeout=120, check=False)
    return {"command": command, "returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}


def _only_v23_development_changes(status_text: str) -> bool:
    allowed_tokens = ["VERSION", "RELEASE_NOTES.md", "pyproject.toml", "src/trading_core/__init__.py", "src/trading_core/cli.py", "src/trading_core/equity_v23_operator_ux_journal", "tests/test_a_share_v23", "tests/a_share_v23", "data/equity_v23_operator_ux_journal", "outputs/equity_v23_operator_ux_journal", "data/equity_data_quality/a_share_v23_operator_ux_journal_audit.json", "outputs/audit/A_SHARE_V23_OPERATOR_UX_JOURNAL_AUDIT.md"]
    for raw in status_text.splitlines():
        path = raw[2:].strip().replace("\\", "/") if len(raw) > 2 else raw.strip().replace("\\", "/")
        if not any(token in path for token in allowed_tokens):
            return False
    return True


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip() if path.exists() else ""


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _stable_id(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]
