"""Audit v0.7.6 A-share virtual portfolio construction artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast, Any

import pandas as pd

from trading_core.equity_data_quality.common import json_safe, read_frame, write_report
from trading_core.equity_portfolios.industry_constraints import industry_cap_violations, max_industry_weight
from trading_core.equity_portfolios.portfolio_config import PORTFOLIO_BOUNDARY, PORTFOLIO_FILES, PORTFOLIO_REPORTS, DEFAULT_AS_OF_DATE, RECOMMENDED_NEXT_VERSION, REMEDIATION_VERSION, TARGET_VERSION
from trading_core.equity_portfolios.portfolio_inputs import portfolio_output_dir
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


FORBIDDEN_POSITIVE_WORDING = [
    '"real_portfolio_generated": true',
    '"buy_sell_signals_generated": true',
    '"order_preview_generated": true',
    '"day2_executed": true',
    '"run_daily_called": true',
    '"broker_connected": true',
    '"real_orders_placed": true',
    '"model_profit_guaranteed": true',
    '"live_trading_ready": true',
    '"not_investment_advice": false',
    '"not_buy_signal": false',
    '"not_sell_signal": false',
    '"not_order_instruction": false',
    '"not_profit_guarantee": false',
    '"not_live_trading_ready": false',
    "guaranteed profit",
    "model can make money",
    "live trading ready: true",
    "strong buy",
    "must buy",
    "broker order generated",
    "real order generated",
    "保证盈利",
    "实盘就绪",
    "强烈买入",
    "必买",
]

DISALLOWED_COLUMNS = {
    "buy_signal",
    "sell_signal",
    "order_preview",
    "broker_order",
    "real_order",
    "trade_instruction",
    "order_instruction",
    "rebalance_instruction",
}


def audit_a_share_virtual_portfolios(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    allow_latest_candidate_date: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    effective_as_of_date, data_dir = _resolve_portfolio_dir(paths, as_of_date, allow_latest_candidate_date)
    output_dir = portfolio_output_dir(paths, effective_as_of_date)
    artifacts = _artifact_paths(data_dir, output_dir)
    config = _load_any(artifacts["portfolio_construction_config"], {})
    manifest = _load_any(artifacts["portfolio_manifest"], {})
    frames = {
        "long_virtual_portfolio": read_frame(artifacts["long_virtual_portfolio_parquet"]),
        "mid_virtual_portfolio": read_frame(artifacts["mid_virtual_portfolio_parquet"]),
        "short_virtual_portfolio": read_frame(artifacts["short_virtual_portfolio_parquet"]),
    }
    candidate_symbols = _candidate_symbols(paths, effective_as_of_date)
    risk_downgraded_symbols = _symbols_from_json(paths.data_dir / "equity_selection" / "daily" / effective_as_of_date / "risk_downgraded_candidates.json")
    excluded_symbols = _symbols_from_json(paths.data_dir / "equity_selection" / "daily" / effective_as_of_date / "excluded_universe.json")
    forbidden_artifacts = _forbidden_artifacts(paths, effective_as_of_date)
    forbidden_wording_hits = _forbidden_wording_hits(artifacts)
    counts = {key.replace("_virtual_portfolio", "_holdings"): len(frame) for key, frame in frames.items()}
    weight_checks = _weight_checks(frames)
    intersections = {
        "risk_downgraded_symbols_included": sorted(_all_symbols(frames).intersection(risk_downgraded_symbols)),
        "excluded_universe_symbols_included": sorted(_all_symbols(frames).intersection(excluded_symbols)),
    }
    checks = _checks(
        artifacts=artifacts,
        config=config,
        manifest=manifest,
        frames=frames,
        candidate_symbols=candidate_symbols,
        intersections=intersections,
        forbidden_artifacts=forbidden_artifacts,
        forbidden_wording_hits=forbidden_wording_hits,
    )
    blocking = [f"{name}=false" for name, passed in checks.items() if not passed]
    payload = {
        "audit_id": "A-SHARE-VIRTUAL-PORTFOLIO-CONSTRUCTION-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": effective_as_of_date,
        "requested_as_of_date": as_of_date,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": _warnings(frames),
        "checks": checks,
        "counts": counts,
        "weight_checks": weight_checks,
        "forbidden_artifacts": forbidden_artifacts,
        "forbidden_wording_hits": forbidden_wording_hits,
        "intersections": intersections,
        "artifacts": {key: str(path) for key, path in artifacts.items()},
        "boundary": dict(PORTFOLIO_BOUNDARY),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION if not blocking else REMEDIATION_VERSION,
    }
    json_path = paths.data_dir / "equity_data_quality" / "a_share_virtual_portfolio_construction_audit.json"
    report_path = paths.outputs_dir / "audit" / "A_SHARE_VIRTUAL_PORTFOLIO_CONSTRUCTION_AUDIT.md"
    return write_report(json_path, json_safe(payload), report_path, _markdown(payload))


def _artifact_paths(data_dir: Path, output_dir: Path) -> dict[str, Path]:
    artifacts = {key: data_dir / filename for key, filename in PORTFOLIO_FILES.items()}
    artifacts.update({key: output_dir / filename for key, filename in PORTFOLIO_REPORTS.items()})
    return artifacts


def _checks(**kwargs: Any) -> dict[str, bool]:
    artifacts: dict[str, Path] = kwargs["artifacts"]
    config = kwargs["config"]
    manifest = kwargs["manifest"]
    frames: dict[str, pd.DataFrame] = kwargs["frames"]
    all_symbols = _all_symbols(frames)
    candidate_symbols = kwargs["candidate_symbols"]
    checks = {
        "portfolio_config_exists": artifacts["portfolio_construction_config"].exists(),
        "portfolio_manifest_exists": artifacts["portfolio_manifest"].exists(),
        "long_virtual_portfolio_exists": artifacts["long_virtual_portfolio_json"].exists() and artifacts["long_virtual_portfolio_parquet"].exists(),
        "mid_virtual_portfolio_exists": artifacts["mid_virtual_portfolio_json"].exists() and artifacts["mid_virtual_portfolio_parquet"].exists(),
        "short_virtual_portfolio_exists": artifacts["short_virtual_portfolio_json"].exists() and artifacts["short_virtual_portfolio_parquet"].exists(),
        "summary_files_exist": artifacts["portfolio_weight_summary"].exists() and artifacts["portfolio_industry_exposure"].exists() and artifacts["portfolio_risk_liquidity_summary"].exists(),
        "portfolio_reports_exist": all(artifacts[key].exists() for key in PORTFOLIO_REPORTS),
        "all_portfolio_symbols_subset_of_candidate_sources": all_symbols.issubset(candidate_symbols),
        "no_risk_downgraded_symbols_in_main_portfolios": not kwargs["intersections"]["risk_downgraded_symbols_included"],
        "no_excluded_universe_symbols_included": not kwargs["intersections"]["excluded_universe_symbols_included"],
        "long_holdings_count_matches_config": len(frames["long_virtual_portfolio"]) == int(config.get("long_holdings", -1)),
        "mid_holdings_count_matches_config": len(frames["mid_virtual_portfolio"]) == int(config.get("mid_holdings", -1)),
        "short_holdings_count_matches_config": len(frames["short_virtual_portfolio"]) == int(config.get("short_holdings", -1)),
        "no_duplicate_symbols_within_each_portfolio": all(_no_duplicates(frame) for frame in frames.values()),
        "weight_sums_approximately_one": all(_weight_sum_ok(frame) for frame in frames.values()),
        "single_stock_weight_caps_respected": _single_caps(frames, config),
        "industry_caps_respected": _industry_caps(frames, config),
        "required_disclaimer_flags_present": _disclaimer_flags_valid(frames),
        "no_buy_sell_signal_artifacts_generated": not kwargs["forbidden_artifacts"]["buy_sell_signal_artifacts_present"],
        "no_order_preview_generated": not kwargs["forbidden_artifacts"]["order_preview_artifacts_present"],
        "no_broker_order_generated": not kwargs["forbidden_artifacts"]["broker_order_artifacts_present"],
        "no_real_order_generated": not kwargs["forbidden_artifacts"]["real_order_artifacts_present"],
        "no_main_orders_trades_accounts_writes": not kwargs["forbidden_artifacts"]["main_ledger_artifacts_present"],
        "no_buy_sell_or_order_columns": not _disallowed_columns(frames),
        "no_profit_guarantee_wording": not kwargs["forbidden_wording_hits"],
        "target_version_matches": manifest.get("target_version") == TARGET_VERSION and config.get("target_version") == TARGET_VERSION,
    }
    for key, expected in PORTFOLIO_BOUNDARY.items():
        checks[f"boundary_{key}_{str(expected).lower()}"] = _boundary(manifest, config, key) is expected
    return checks


def _weight_checks(frames: dict[str, pd.DataFrame]) -> dict[str, float]:
    checks = {}
    for key, frame in frames.items():
        prefix = key.replace("_virtual_portfolio", "")
        checks[f"{prefix}_weight_sum"] = round(float(frame["target_weight"].sum()) if "target_weight" in frame.columns else 0.0, 6)
        checks[f"{prefix}_max_single_weight"] = round(float(frame["target_weight"].max()) if "target_weight" in frame.columns and not frame.empty else 0.0, 6)
        checks[f"{prefix}_max_industry_weight"] = round(max_industry_weight(cast(list[dict[str, Any]], frame.to_dict("records"))), 6)
    return checks


def _single_caps(frames: dict[str, pd.DataFrame], config: dict[str, Any]) -> bool:
    caps = {
        "long_virtual_portfolio": float(config.get("long_max_single_weight", 0.0)),
        "mid_virtual_portfolio": float(config.get("mid_max_single_weight", 0.0)),
        "short_virtual_portfolio": float(config.get("short_max_single_weight", 0.0)),
    }
    return all(
        not frame.empty and "target_weight" in frame.columns and float(frame["target_weight"].max()) <= caps[key] + 1e-8 and (frame["target_weight"] > 0).all()
        for key, frame in frames.items()
    )


def _industry_caps(frames: dict[str, pd.DataFrame], config: dict[str, Any]) -> bool:
    caps = {
        "long_virtual_portfolio": float(config.get("long_max_industry_weight", 0.0)),
        "mid_virtual_portfolio": float(config.get("mid_max_industry_weight", 0.0)),
        "short_virtual_portfolio": float(config.get("short_max_industry_weight", 0.0)),
    }
    return all(not industry_cap_violations(cast(list[dict[str, Any]], frame.to_dict("records")), caps[key]) for key, frame in frames.items())


def _disclaimer_flags_valid(frames: dict[str, pd.DataFrame]) -> bool:
    flags = [
        "virtual_only",
        "research_only",
        "not_investment_advice",
        "not_buy_signal",
        "not_sell_signal",
        "not_order_instruction",
        "not_profit_guarantee",
        "not_live_trading_ready",
    ]
    for frame in frames.values():
        if frame.empty:
            return False
        for flag in flags:
            if flag not in frame.columns or not frame[flag].fillna(False).astype(bool).all():
                return False
    return True


def _forbidden_artifacts(paths: ProjectPaths, as_of_date: str) -> dict[str, list[str]]:
    templates = {
        "buy_sell_signal_artifacts_present": [
            "outputs/equity_portfolios/daily/{date}/BUY_LIST.md",
            "outputs/equity_portfolios/daily/{date}/SELL_LIST.md",
            "data/equity_portfolios/daily/{date}/buy_list.json",
            "data/equity_portfolios/daily/{date}/sell_list.json",
        ],
        "order_preview_artifacts_present": [
            "outputs/equity_portfolios/daily/{date}/ORDER_PREVIEW.md",
            "data/equity_portfolios/daily/{date}/order_preview.json",
            "data/equity_portfolios/daily/{date}/orders.json",
        ],
        "broker_order_artifacts_present": [
            "data/equity_portfolios/daily/{date}/BROKER_ORDER.json",
            "data/equity_portfolios/daily/{date}/broker_order.json",
            "outputs/equity_portfolios/daily/{date}/BROKER_ORDER.md",
        ],
        "real_order_artifacts_present": [
            "data/equity_portfolios/daily/{date}/REAL_ORDER.json",
            "data/equity_portfolios/daily/{date}/real_order.json",
            "outputs/equity_portfolios/daily/{date}/REAL_ORDER.md",
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


def _forbidden_wording_hits(artifacts: dict[str, Path]) -> list[str]:
    hits = []
    for _key, path in artifacts.items():
        if not path.exists() or path.suffix not in {".json", ".md"}:
            continue
        text = path.read_text(encoding="utf-8").lower()
        for phrase in FORBIDDEN_POSITIVE_WORDING:
            if phrase.lower() in text:
                hits.append(f"{path.name}:{phrase}")
    return hits


def _resolve_portfolio_dir(paths: ProjectPaths, as_of_date: str, allow_latest: bool) -> tuple[str, Path]:
    base = paths.data_dir / "equity_portfolios" / "daily"
    exact = base / as_of_date
    if (exact / PORTFOLIO_FILES["portfolio_manifest"]).exists():
        return as_of_date, exact
    if not allow_latest:
        return as_of_date, exact
    candidates = sorted(path for path in base.glob("*") if path.is_dir() and path.name <= as_of_date and (path / PORTFOLIO_FILES["portfolio_manifest"]).exists())
    if not candidates:
        return as_of_date, exact
    selected = candidates[-1]
    return selected.name, selected


def _candidate_symbols(paths: ProjectPaths, as_of_date: str) -> set[str]:
    base = paths.data_dir / "equity_selection" / "daily" / as_of_date
    symbols: set[str] = set()
    for name in ["long_candidates.json", "mid_candidates.json", "short_candidates.json", "multi_horizon_candidates.json"]:
        symbols.update(_symbols_from_json(base / name))
    return symbols


def _symbols_from_json(path: Path) -> set[str]:
    rows = _load_any(path, [])
    if not isinstance(rows, list):
        return set()
    return {str(row.get("symbol")) for row in rows if isinstance(row, dict) and row.get("symbol")}


def _load_any(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _all_symbols(frames: dict[str, pd.DataFrame]) -> set[str]:
    symbols: set[str] = set()
    for frame in frames.values():
        if not frame.empty and "symbol" in frame.columns:
            symbols.update(frame["symbol"].dropna().astype(str))
    return symbols


def _no_duplicates(frame: pd.DataFrame) -> bool:
    return not frame.empty and "symbol" in frame.columns and not frame["symbol"].duplicated().any()


def _weight_sum_ok(frame: pd.DataFrame) -> bool:
    if frame.empty or "target_weight" not in frame.columns:
        return False
    total = float(frame["target_weight"].sum())
    return 0.999 <= total <= 1.001


def _disallowed_columns(frames: dict[str, pd.DataFrame]) -> list[str]:
    hits = []
    for frame in frames.values():
        for column in frame.columns:
            if column in DISALLOWED_COLUMNS:
                hits.append(column)
    return sorted(set(hits))


def _boundary(manifest: dict[str, Any], config: dict[str, Any], key: str) -> Any:
    values = []
    for payload in [manifest, config]:
        boundary = payload.get("boundary") if isinstance(payload, dict) else {}
        if boundary:
            values.append(boundary.get(key))
    if not values:
        return None
    first = values[0]
    if any(value is not first for value in values):
        return "__boundary_mismatch__"
    return first


def _warnings(frames: dict[str, pd.DataFrame]) -> list[str]:
    warnings = []
    for key, frame in frames.items():
        if "industry_level_1" in frame.columns and (frame["industry_level_1"].astype(str).str.lower() == "unclassified").any():
            warnings.append(f"{key}: raw industry_level_1 contains Unclassified; audit uses industry fallback buckets for caps")
    return warnings


def _markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# A-Share Virtual Portfolio Construction Audit",
            "",
            f"- target_version: {payload['target_version']}",
            f"- as_of_date: {payload['as_of_date']}",
            f"- overall_passed: {str(payload['overall_passed']).lower()}",
            f"- blocking_reasons: {payload['blocking_reasons']}",
            f"- warnings: {len(payload['warnings'])}",
            f"- counts: {payload['counts']}",
            f"- weight_checks: {payload['weight_checks']}",
            f"- forbidden_artifacts: {payload['forbidden_artifacts']}",
            "",
            "## Boundary",
            "- Virtual portfolio construction only.",
            "- Virtual portfolios generated: true.",
            "- No real portfolio generated.",
            "- No buy/sell signals generated.",
            "- No order preview generated.",
            "- Official forward dry-run status unchanged.",
            "- Day2 was not executed.",
            "- run-daily was not called.",
            "- No broker is connected.",
            "- No real orders were placed.",
            "- This is not a model profit guarantee.",
            "- Live trading ready: false.",
            "- Virtual target weights are research-only and not order instructions.",
            "",
            f"Recommended next version: {payload['recommended_next_version']}",
            "",
        ]
    )
