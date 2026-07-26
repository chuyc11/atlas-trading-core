"""Audit v0.7.7 A-share daily stock selection briefing artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from trading_core.equity_briefings.briefing_config import (
    BRIEFING_BOUNDARY,
    BRIEFING_FILES,
    BRIEFING_REPORTS,
    DEFAULT_AS_OF_DATE,
    FORBIDDEN_BRIEFING_WORDING,
    NEGATIVE_CONTEXT_ALLOWLIST,
    RECOMMENDED_NEXT_VERSION,
    REMEDIATION_VERSION,
    REQUIRED_SECTION_KEYS,
    SOURCE_TRACE_SECTION_KEYS,
    TARGET_VERSION,
)
from trading_core.equity_briefings.briefing_inputs import briefing_output_dir
from trading_core.equity_data_quality.common import json_safe, sha256_file, write_report
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def audit_a_share_daily_stock_selection_briefing(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    allow_latest_artifact_date: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    effective_as_of_date, data_dir = _resolve_briefing_dir(paths, as_of_date, allow_latest_artifact_date)
    output_dir = briefing_output_dir(paths, effective_as_of_date)
    artifacts = _artifact_paths(data_dir, output_dir)
    briefing = _load_any(artifacts["daily_stock_selection_briefing"], {})
    manifest = _load_any(artifacts["briefing_manifest"], {})
    source_trace = _load_any(artifacts["briefing_source_trace"], {})
    boundary_check = _load_any(artifacts["briefing_boundary_check"], {})
    required_sections = _required_sections(briefing)
    source_trace_sections = _source_trace_sections(source_trace, paths)
    forbidden_wording_hits = _forbidden_wording_hits(artifacts)
    forbidden_artifacts = _forbidden_artifacts(paths, effective_as_of_date)
    checks = _checks(
        artifacts=artifacts,
        briefing=briefing,
        manifest=manifest,
        source_trace=source_trace,
        boundary_check=boundary_check,
        required_sections=required_sections,
        source_trace_sections=source_trace_sections,
        forbidden_wording_hits=forbidden_wording_hits,
        forbidden_artifacts=forbidden_artifacts,
    )
    blocking = [f"{name}=false" for name, passed in checks.items() if not passed]
    payload = {
        "audit_id": "A-SHARE-DAILY-STOCK-SELECTION-BRIEFING-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": effective_as_of_date,
        "requested_as_of_date": as_of_date,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": _warnings(briefing),
        "required_sections": required_sections,
        "source_trace_sections": source_trace_sections,
        "checks": checks,
        "forbidden_wording_hits": forbidden_wording_hits,
        "forbidden_artifacts": forbidden_artifacts,
        "boundary": dict(BRIEFING_BOUNDARY),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION if not blocking else REMEDIATION_VERSION,
    }
    json_path = paths.data_dir / "equity_data_quality" / "a_share_daily_stock_selection_briefing_audit.json"
    report_path = paths.outputs_dir / "audit" / "A_SHARE_DAILY_STOCK_SELECTION_BRIEFING_AUDIT.md"
    return write_report(json_path, json_safe(payload), report_path, _markdown(payload))


def _artifact_paths(data_dir: Path, output_dir: Path) -> dict[str, Path]:
    return {
        "daily_stock_selection_briefing": data_dir / BRIEFING_FILES["daily_stock_selection_briefing"],
        "briefing_manifest": data_dir / BRIEFING_FILES["briefing_manifest"],
        "briefing_source_trace": data_dir / BRIEFING_FILES["briefing_source_trace"],
        "briefing_boundary_check": data_dir / BRIEFING_FILES["briefing_boundary_check"],
        "daily_stock_selection_briefing_report": output_dir / BRIEFING_REPORTS["daily_stock_selection_briefing_report"],
        "briefing_source_trace_report": output_dir / BRIEFING_REPORTS["briefing_source_trace_report"],
    }


def _checks(**kwargs: Any) -> dict[str, bool]:
    artifacts: dict[str, Path] = kwargs["artifacts"]
    briefing = kwargs["briefing"]
    manifest = kwargs["manifest"]
    source_trace = kwargs["source_trace"]
    boundary_check = kwargs["boundary_check"]
    source_trace_sections = kwargs["source_trace_sections"]
    required_sections = kwargs["required_sections"]
    checks = {
        "briefing_json_exists": artifacts["daily_stock_selection_briefing"].exists(),
        "briefing_markdown_exists": artifacts["daily_stock_selection_briefing_report"].exists(),
        "briefing_manifest_exists": artifacts["briefing_manifest"].exists(),
        "source_trace_exists": artifacts["briefing_source_trace"].exists() and artifacts["briefing_source_trace_report"].exists(),
        "boundary_check_exists": artifacts["briefing_boundary_check"].exists(),
        "all_required_sections_exist": all(required_sections.values()),
        "top10_long_section_exists": required_sections["long_candidates_top10"],
        "top10_mid_section_exists": required_sections["mid_candidates_top10"],
        "top10_short_section_exists": required_sections["short_candidates_top10"],
        "multi_horizon_section_exists": required_sections["multi_horizon_candidates"],
        "risk_downgraded_section_exists": required_sections["risk_downgraded_candidates"],
        "virtual_portfolio_section_exists": required_sections["virtual_portfolio_summary"],
        "industry_exposure_section_exists": required_sections["industry_exposure_summary"],
        "risk_liquidity_section_exists": required_sections["risk_liquidity_summary"],
        "do_not_misread_section_exists": required_sections["do_not_misread"],
        "source_trace_complete": bool(source_trace.get("source_trace_complete")) and all(source_trace_sections.values()),
        "source_trace_covers_every_section": set(source_trace_sections) == set(SOURCE_TRACE_SECTION_KEYS),
        "source_hashes_match": _source_hashes_match(source_trace, artifacts["briefing_source_trace"]),
        "manifest_artifact_hashes_match": _manifest_artifact_hashes_match(manifest, artifacts["briefing_manifest"]),
        "upstream_audit_dates_match_briefing": briefing.get("audit_status", {}).get("all_audits_current") is True,
        "input_manifest_dates_match_briefing": briefing.get("quality_gate", {}).get("input_manifest_dates_match") is True,
        "portfolio_weight_sums_valid": _portfolio_weight_sums_valid(briefing),
        "briefing_reads_from_existing_artifacts": _reads_from_existing_artifacts(source_trace),
        "no_forbidden_wording": not kwargs["forbidden_wording_hits"],
        "no_buy_sell_signal_artifacts_generated": not kwargs["forbidden_artifacts"]["buy_sell_signal_artifacts_present"],
        "no_order_preview_generated": not kwargs["forbidden_artifacts"]["order_preview_artifacts_present"],
        "no_broker_order_generated": not kwargs["forbidden_artifacts"]["broker_order_artifacts_present"],
        "no_real_order_generated": not kwargs["forbidden_artifacts"]["real_order_artifacts_present"],
        "no_main_orders_trades_accounts_writes": not kwargs["forbidden_artifacts"]["main_ledger_artifacts_present"],
        "target_version_matches": briefing.get("target_version") == TARGET_VERSION and manifest.get("target_version") == TARGET_VERSION,
        "recommended_next_version_matches": briefing.get("recommended_next_version") == RECOMMENDED_NEXT_VERSION,
        "scores_regenerated_false": _boundary(briefing, manifest, boundary_check, "scores_regenerated") is False,
        "candidates_regenerated_false": _boundary(briefing, manifest, boundary_check, "candidates_regenerated") is False,
        "virtual_portfolios_regenerated_false": _boundary(briefing, manifest, boundary_check, "virtual_portfolios_regenerated") is False,
        "buy_sell_signals_generated_false": _boundary(briefing, manifest, boundary_check, "buy_sell_signals_generated") is False,
        "order_preview_generated_false": _boundary(briefing, manifest, boundary_check, "order_preview_generated") is False,
        "broker_connected_false": _boundary(briefing, manifest, boundary_check, "broker_connected") is False,
        "real_orders_placed_false": _boundary(briefing, manifest, boundary_check, "real_orders_placed") is False,
        "model_profit_guaranteed_false": _boundary(briefing, manifest, boundary_check, "model_profit_guaranteed") is False,
        "live_trading_ready_false": _boundary(briefing, manifest, boundary_check, "live_trading_ready") is False,
    }
    for key, expected in BRIEFING_BOUNDARY.items():
        checks[f"boundary_{key}_{str(expected).lower()}"] = _boundary(briefing, manifest, boundary_check, key) is expected
    return checks


def _required_sections(briefing: dict[str, Any]) -> dict[str, bool]:
    sections = {}
    for audit_key, payload_key in REQUIRED_SECTION_KEYS.items():
        value = briefing.get(payload_key)
        if isinstance(value, list):
            sections[audit_key] = bool(value)
        elif isinstance(value, dict):
            sections[audit_key] = bool(value)
        else:
            sections[audit_key] = value not in (None, "")
    return sections


def _source_trace_sections(source_trace: dict[str, Any], paths: ProjectPaths) -> dict[str, bool]:
    sections = {}
    trace_sections = source_trace.get("sections", {})
    for key in SOURCE_TRACE_SECTION_KEYS:
        record = trace_sections.get(key, {})
        source_paths = record.get("source_paths", [])
        sections[key] = bool(record.get("complete")) and bool(source_paths) and all((paths.project_root / source).exists() for source in source_paths)
    return sections


def _source_hashes_match(source_trace: dict[str, Any], trace_path: Path) -> bool:
    if not trace_path.exists():
        return False
    for section in source_trace.get("sections", {}).values():
        for record in section.get("sources", []):
            path = trace_path.parents[4] / str(record.get("path", ""))
            if not path.exists() or record.get("sha256") != sha256_file(path):
                return False
    return bool(source_trace.get("sections"))


def _manifest_artifact_hashes_match(manifest: dict[str, Any], manifest_path: Path) -> bool:
    if not manifest_path.exists() or not manifest.get("artifacts"):
        return False
    project_root = manifest_path.parents[4]
    for record in manifest.get("artifacts", {}).values():
        path = project_root / str(record.get("path", ""))
        if not path.exists() or record.get("exists") is not True or record.get("sha256") != sha256_file(path):
            return False
    return True


def _portfolio_weight_sums_valid(briefing: dict[str, Any]) -> bool:
    portfolios = briefing.get("virtual_portfolios", {})
    if set(portfolios) != {"long", "mid", "short"}:
        return False
    try:
        return all(abs(float(record.get("weight_sum")) - 1.0) <= 0.001 for record in portfolios.values())
    except (TypeError, ValueError):
        return False


def _reads_from_existing_artifacts(source_trace: dict[str, Any]) -> bool:
    sections = source_trace.get("sections", {})
    for record in sections.values():
        for source in record.get("source_paths", []):
            text = str(source)
            if text.startswith("data/equity_briefings/") or text.startswith("outputs/equity_briefings/"):
                return False
            if not (
                text.startswith("data/equity_selection/")
                or text.startswith("data/equity_scores/")
                or text.startswith("data/equity_features/")
                or text.startswith("data/equity_portfolios/")
                or text.startswith("data/equity_data_quality/")
            ):
                return False
    return bool(sections)


def _forbidden_wording_hits(artifacts: dict[str, Path]) -> list[str]:
    hits = []
    for key in ["daily_stock_selection_briefing", "daily_stock_selection_briefing_report"]:
        path = artifacts[key]
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        lower = text.lower()
        for phrase in FORBIDDEN_BRIEFING_WORDING:
            phrase_lower = phrase.lower()
            start = 0
            while True:
                index = lower.find(phrase_lower, start)
                if index < 0:
                    break
                window = lower[max(0, index - 16) : index + len(phrase_lower) + 16]
                if not _negative_context_allowed(window):
                    hits.append(f"{path.name}:{phrase}")
                start = index + len(phrase_lower)
    return sorted(set(hits))


def _negative_context_allowed(window: str) -> bool:
    return any(allowed.lower() in window for allowed in NEGATIVE_CONTEXT_ALLOWLIST)


def _forbidden_artifacts(paths: ProjectPaths, as_of_date: str) -> dict[str, list[str]]:
    templates = {
        "buy_sell_signal_artifacts_present": [
            "outputs/equity_briefings/daily/{date}/BUY_LIST.md",
            "outputs/equity_briefings/daily/{date}/SELL_LIST.md",
            "data/equity_briefings/daily/{date}/buy_list.json",
            "data/equity_briefings/daily/{date}/sell_list.json",
        ],
        "order_preview_artifacts_present": [
            "outputs/equity_briefings/daily/{date}/ORDER_PREVIEW.md",
            "data/equity_briefings/daily/{date}/order_preview.json",
            "data/equity_briefings/daily/{date}/orders.json",
        ],
        "broker_order_artifacts_present": [
            "data/equity_briefings/daily/{date}/BROKER_ORDER.json",
            "data/equity_briefings/daily/{date}/broker_order.json",
            "outputs/equity_briefings/daily/{date}/BROKER_ORDER.md",
        ],
        "real_order_artifacts_present": [
            "data/equity_briefings/daily/{date}/REAL_ORDER.json",
            "data/equity_briefings/daily/{date}/real_order.json",
            "outputs/equity_briefings/daily/{date}/REAL_ORDER.md",
        ],
        "main_ledger_artifacts_present": [
            "data/orders/orders-{date}.jsonl",
            "data/trades/trades-{date}.jsonl",
            "data/accounts/account-{date}.json",
            "data/portfolio/portfolio-{date}.jsonl",
            "data/portfolios/portfolio-{date}.jsonl",
        ],
    }
    result = {}
    for key, items in templates.items():
        present = []
        for template in items:
            path = paths.project_root / template.format(date=as_of_date)
            if path.exists():
                present.append(str(path))
        result[key] = present
    return result


def _boundary(briefing: dict[str, Any], manifest: dict[str, Any], boundary_check: dict[str, Any], key: str) -> Any:
    values = []
    for payload in [briefing, manifest, boundary_check]:
        if key in payload:
            values.append(payload.get(key))
        boundary = payload.get("boundary") if isinstance(payload, dict) else {}
        if key in boundary:
            values.append(boundary.get(key))
    if not values:
        return None
    first = values[0]
    if any(value is not first for value in values):
        return "__boundary_mismatch__"
    return first


def _warnings(briefing: dict[str, Any]) -> list[str]:
    warnings = []
    industry = briefing.get("industry_exposure_summary", {})
    if industry.get("unclassified_fallback_warning"):
        warnings.append("raw industry_level_1 contains Unclassified; briefing disclosed fallback industry bucket usage")
    for warning in briefing.get("audit_status", {}).get("warnings", []):
        warnings.append(str(warning))
    return sorted(set(warnings))


def _resolve_briefing_dir(paths: ProjectPaths, as_of_date: str, allow_latest: bool) -> tuple[str, Path]:
    base = paths.data_dir / "equity_briefings" / "daily"
    exact = base / as_of_date
    if (exact / BRIEFING_FILES["daily_stock_selection_briefing"]).exists():
        return as_of_date, exact
    if not allow_latest:
        return as_of_date, exact
    candidates = sorted(path for path in base.glob("*") if path.is_dir() and path.name <= as_of_date and (path / BRIEFING_FILES["daily_stock_selection_briefing"]).exists())
    if not candidates:
        return as_of_date, exact
    selected = candidates[-1]
    return selected.name, selected


def _load_any(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# A-Share Daily Stock Selection Briefing Audit",
            "",
            f"- target_version: {payload['target_version']}",
            f"- as_of_date: {payload['as_of_date']}",
            f"- overall_passed: {str(payload['overall_passed']).lower()}",
            f"- blocking_reasons: {payload['blocking_reasons']}",
            f"- warnings: {len(payload['warnings'])}",
            f"- required_sections: {payload['required_sections']}",
            f"- source_trace_complete: {payload['checks'].get('source_trace_complete')}",
            "",
            "## Boundary",
            "- Briefing only.",
            "- Scores regenerated: false.",
            "- Candidates regenerated: false.",
            "- Virtual portfolios regenerated: false.",
            "- Buy/sell signals generated: false.",
            "- Order preview generated: false.",
            "- Official forward dry-run status unchanged.",
            "- Day2 was not executed.",
            "- run-daily was not called.",
            "- No broker is connected.",
            "- No real orders were placed.",
            "- This is not a model profit guarantee.",
            "- Live trading ready: false.",
            "",
            f"Recommended next version: {payload['recommended_next_version']}",
            "",
        ]
    )
