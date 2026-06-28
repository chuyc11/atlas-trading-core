"""Audit v0.7.8 A-share virtual portfolio tracking artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import json_safe, write_report
from trading_core.equity_portfolio_tracking.tracking_config import (
    ALLOWED_LEDGER_RECORD_TYPES,
    DEFAULT_AS_OF_DATE,
    FORBIDDEN_LEDGER_RECORD_TYPES,
    PORTFOLIO_KEYS,
    RECOMMENDED_NEXT_VERSION,
    REMEDIATION_VERSION,
    TARGET_VERSION,
    TRACKING_BOUNDARY,
    TRACKING_FILES,
    TRACKING_REPORTS,
)
from trading_core.equity_portfolio_tracking.tracking_inputs import load_tracking_inputs, tracking_data_dir, tracking_output_dir
from trading_core.equity_portfolio_tracking.tracking_report import render_tracking_audit
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
    '"not_order_instruction": false',
    '"not_real_trade": false',
    '"not_profit_guarantee": false',
    '"not_live_trading_ready": false',
    "guaranteed profit",
    "model can make money",
    "live trading ready: true",
    "strong buy",
    "must buy",
    "broker order generated",
    "real order generated",
    '"record_type": "buy_order"',
    '"record_type": "sell_order"',
    '"record_type": "broker_fill"',
    '"record_type": "order_preview"',
    '"record_type": "real_trade"',
    "保证盈利",
    "实盘就绪",
    "强烈买入",
    "必买",
]

DISALLOWED_REAL_ACCOUNT_FIELDS = {
    "account_id",
    "broker_account_id",
    "real_account_id",
    "broker_position_id",
    "broker_cash",
    "broker_equity",
    "real_position",
    "real_account_balance",
    "real_cash_balance",
    "trade_instruction",
    "rebalance_instruction",
    "order_instruction",
    "buy_signal",
    "sell_signal",
}


def audit_a_share_virtual_portfolio_tracking(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    data_dir = tracking_data_dir(paths, as_of_date)
    output_dir = tracking_output_dir(paths, as_of_date)
    artifacts = _artifact_paths(data_dir, output_dir)
    config = _load_any(artifacts["tracking_config"], {})
    manifest = _load_any(artifacts["tracking_manifest"], {})
    source_trace = _load_any(artifacts["tracking_source_trace"], {})
    summary = _load_any(artifacts["tracking_summary"], {})
    ledgers = {key: _load_any(artifacts[f"{key}_paper_ledger"], []) for key in PORTFOLIO_KEYS}
    holdings = {key: _load_any(artifacts[f"{key}_holdings_snapshot"], {}) for key in PORTFOLIO_KEYS}
    nav = _load_any(artifacts["portfolio_nav_snapshot"], {})
    performance = _load_any(artifacts["portfolio_performance_snapshot"], {})
    exposure = _load_any(artifacts["portfolio_exposure_snapshot"], {})
    benchmark = _load_any(artifacts["benchmark_comparison_snapshot"], {})

    input_error = ""
    inputs = None
    try:
        inputs = load_tracking_inputs(paths=paths, as_of_date=as_of_date)
    except ValueError as exc:
        input_error = str(exc)

    forbidden_artifacts = _forbidden_artifacts(paths, as_of_date)
    forbidden_wording_hits = _forbidden_wording_hits(artifacts)
    real_account_fields = sorted(set(_field_hits([config, manifest, source_trace, summary, nav, performance, exposure, benchmark, *ledgers.values(), *holdings.values()])))
    counts = _counts(ledgers, holdings)
    nav_checks = _nav_checks(nav)
    symbol_checks = _symbol_checks(inputs, ledgers, holdings) if inputs is not None else {f"{key}_symbols_match": False for key in PORTFOLIO_KEYS}
    risk_excluded = _risk_excluded_intersections(inputs, holdings) if inputs is not None else {"risk_downgraded_symbols_included": [], "excluded_universe_symbols_included": []}
    checks = _checks(
        artifacts=artifacts,
        config=config,
        manifest=manifest,
        source_trace=source_trace,
        summary=summary,
        ledgers=ledgers,
        holdings=holdings,
        nav=nav,
        performance=performance,
        exposure=exposure,
        benchmark=benchmark,
        input_error=input_error,
        symbol_checks=symbol_checks,
        nav_checks=nav_checks,
        forbidden_artifacts=forbidden_artifacts,
        forbidden_wording_hits=forbidden_wording_hits,
        real_account_fields=real_account_fields,
        risk_excluded=risk_excluded,
    )
    blocking = [f"{name}=false" for name, passed in checks.items() if not passed]
    payload = {
        "audit_id": "A-SHARE-VIRTUAL-PORTFOLIO-TRACKING-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": _warnings(benchmark, summary),
        "counts": counts,
        "nav_checks": nav_checks,
        "checks": checks,
        "input_error": input_error,
        "symbol_checks": symbol_checks,
        "risk_excluded_intersections": risk_excluded,
        "forbidden_artifacts": forbidden_artifacts,
        "forbidden_wording_hits": forbidden_wording_hits,
        "real_account_field_hits": real_account_fields,
        "boundary": {
            "virtual_tracking_only": True,
            "paper_ledger_generated": True,
            "real_portfolio_generated": False,
            "buy_sell_signals_generated": False,
            "order_preview_generated": False,
            "official_forward_dry_run_status_unchanged": True,
            "day2_executed": False,
            "run_daily_called": False,
            "broker_connected": False,
            "real_orders_placed": False,
            "model_profit_guaranteed": False,
            "live_trading_ready": False,
        },
        "recommended_next_version": RECOMMENDED_NEXT_VERSION if not blocking else REMEDIATION_VERSION,
    }
    json_path = paths.data_dir / "equity_data_quality" / "a_share_virtual_portfolio_tracking_audit.json"
    report_path = paths.outputs_dir / "audit" / "A_SHARE_VIRTUAL_PORTFOLIO_TRACKING_AUDIT.md"
    return write_report(json_path, json_safe(payload), report_path, render_tracking_audit(payload))


def _artifact_paths(data_dir: Path, output_dir: Path) -> dict[str, Path]:
    artifacts = {key: data_dir / filename for key, filename in TRACKING_FILES.items()}
    artifacts.update({key: output_dir / filename for key, filename in TRACKING_REPORTS.items()})
    return artifacts


def _checks(**kwargs: Any) -> dict[str, bool]:
    artifacts: dict[str, Path] = kwargs["artifacts"]
    config = kwargs["config"]
    manifest = kwargs["manifest"]
    source_trace = kwargs["source_trace"]
    summary = kwargs["summary"]
    ledgers = kwargs["ledgers"]
    holdings = kwargs["holdings"]
    nav = kwargs["nav"]
    performance = kwargs["performance"]
    exposure = kwargs["exposure"]
    benchmark = kwargs["benchmark"]
    checks = {
        "tracking_inputs_available": not kwargs["input_error"],
        "tracking_config_exists": artifacts["tracking_config"].exists(),
        "tracking_manifest_exists": artifacts["tracking_manifest"].exists(),
        "long_mid_short_paper_ledgers_exist": all(artifacts[f"{key}_paper_ledger"].exists() for key in PORTFOLIO_KEYS),
        "long_mid_short_holdings_snapshots_exist": all(artifacts[f"{key}_holdings_snapshot"].exists() for key in PORTFOLIO_KEYS),
        "nav_snapshot_exists": artifacts["portfolio_nav_snapshot"].exists(),
        "performance_snapshot_exists": artifacts["portfolio_performance_snapshot"].exists(),
        "exposure_snapshot_exists": artifacts["portfolio_exposure_snapshot"].exists(),
        "benchmark_comparison_snapshot_exists": artifacts["benchmark_comparison_snapshot"].exists(),
        "source_trace_exists": artifacts["tracking_source_trace"].exists(),
        "source_trace_complete": bool(source_trace.get("source_trace_complete")),
        "all_portfolio_symbols_match_v076": all(kwargs["symbol_checks"].values()),
        "initial_virtual_capital_recorded": _initial_capital_recorded(config, ledgers),
        "weight_sums_approximately_one": all(_weight_sum_ok(kwargs["nav_checks"].get(f"{key}_weight_sum", 0.0)) for key in PORTFOLIO_KEYS),
        "nav_equals_cash_plus_holdings_market_value": _nav_arithmetic_ok(nav),
        "no_duplicate_holdings": all(_no_duplicate_holdings(holdings.get(key, {})) for key in PORTFOLIO_KEYS),
        "no_risk_downgraded_symbols_introduced": not kwargs["risk_excluded"]["risk_downgraded_symbols_included"],
        "no_excluded_universe_symbols_introduced": not kwargs["risk_excluded"]["excluded_universe_symbols_included"],
        "no_real_account_fields_present": not kwargs["real_account_fields"],
        "no_buy_sell_signal_artifacts_generated": not kwargs["forbidden_artifacts"]["buy_sell_signal_artifacts_present"],
        "no_order_preview_generated": not kwargs["forbidden_artifacts"]["order_preview_artifacts_present"],
        "no_broker_order_generated": not kwargs["forbidden_artifacts"]["broker_order_artifacts_present"],
        "no_real_order_generated": not kwargs["forbidden_artifacts"]["real_order_artifacts_present"],
        "no_main_orders_trades_accounts_writes": not kwargs["forbidden_artifacts"]["main_ledger_artifacts_present"],
        "no_profit_guarantee_wording": not kwargs["forbidden_wording_hits"],
        "no_live_trading_ready_wording": not kwargs["forbidden_wording_hits"],
        "ledger_record_types_allowed": _ledger_record_types_allowed(ledgers),
        "target_version_matches": config.get("target_version") == TARGET_VERSION and manifest.get("target_version") == TARGET_VERSION and summary.get("target_version") == TARGET_VERSION,
        "first_day_initialization_recorded": bool(performance.get("first_day_initialization")) and bool(benchmark.get("first_day_initialization")),
        "performance_not_yet_observed_recorded": bool(performance.get("performance_not_yet_observed")) and bool(benchmark.get("performance_not_yet_observed")),
    }
    for key, expected in TRACKING_BOUNDARY.items():
        checks[f"boundary_{key}_{str(expected).lower()}"] = _boundary(config, manifest, summary, key) is expected
    return checks


def _counts(ledgers: dict[str, list[dict[str, Any]]], holdings: dict[str, dict[str, Any]]) -> dict[str, int]:
    counts = {}
    for key in PORTFOLIO_KEYS:
        counts[f"{key}_holdings"] = len(holdings.get(key, {}).get("holdings", []))
        counts[f"{key}_ledger_records"] = len(ledgers.get(key, []))
    return counts


def _nav_checks(nav: dict[str, Any]) -> dict[str, float]:
    result = {}
    portfolios = nav.get("portfolios", {})
    for key in PORTFOLIO_KEYS:
        record = portfolios.get(key, {})
        result[f"{key}_nav"] = round(float(record.get("portfolio_nav") or 0.0), 6)
        result[f"{key}_weight_sum"] = round(float(record.get("weight_sum") or 0.0), 6)
    return result


def _symbol_checks(inputs, ledgers: dict[str, list[dict[str, Any]]], holdings: dict[str, dict[str, Any]]) -> dict[str, bool]:
    checks = {}
    for key in PORTFOLIO_KEYS:
        source_symbols = {str(row.get("symbol")) for row in inputs.portfolios[key] if row.get("symbol")}
        ledger_symbols = {str(row.get("symbol")) for row in ledgers.get(key, []) if row.get("symbol")}
        holding_symbols = {str(row.get("symbol")) for row in holdings.get(key, {}).get("holdings", []) if row.get("symbol")}
        checks[f"{key}_symbols_match"] = source_symbols == ledger_symbols == holding_symbols
    return checks


def _risk_excluded_intersections(inputs, holdings: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    symbols = set()
    for snapshot in holdings.values():
        symbols.update(str(row.get("symbol")) for row in snapshot.get("holdings", []) if row.get("symbol"))
    return {
        "risk_downgraded_symbols_included": sorted(symbols.intersection(inputs.risk_downgraded_symbols)),
        "excluded_universe_symbols_included": sorted(symbols.intersection(inputs.excluded_symbols)),
    }


def _initial_capital_recorded(config: dict[str, Any], ledgers: dict[str, list[dict[str, Any]]]) -> bool:
    capital = config.get("initial_virtual_capital", {})
    if not all(float(capital.get(key, 0.0) or 0.0) > 0.0 for key in PORTFOLIO_KEYS):
        return False
    for key, rows in ledgers.items():
        if not rows:
            return False
        if not all("virtual_position_value" in row for row in rows):
            return False
    return True


def _weight_sum_ok(value: float) -> bool:
    return 0.999 <= float(value) <= 1.001


def _nav_arithmetic_ok(nav: dict[str, Any]) -> bool:
    for record in nav.get("portfolios", {}).values():
        lhs = float(record.get("portfolio_nav") or 0.0)
        rhs = float(record.get("cash_balance") or 0.0) + float(record.get("holdings_market_value") or 0.0)
        if abs(lhs - rhs) > 1e-4:
            return False
    return bool(nav.get("portfolios"))


def _no_duplicate_holdings(snapshot: dict[str, Any]) -> bool:
    symbols = [str(row.get("symbol")) for row in snapshot.get("holdings", []) if row.get("symbol")]
    return bool(symbols) and len(symbols) == len(set(symbols))


def _ledger_record_types_allowed(ledgers: dict[str, list[dict[str, Any]]]) -> bool:
    for rows in ledgers.values():
        if not rows:
            return False
        for row in rows:
            record_type = str(row.get("record_type") or "")
            if record_type in FORBIDDEN_LEDGER_RECORD_TYPES or record_type not in ALLOWED_LEDGER_RECORD_TYPES:
                return False
    return True


def _boundary(config: dict[str, Any], manifest: dict[str, Any], summary: dict[str, Any], key: str) -> Any:
    values = []
    for payload in [config, manifest, summary]:
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


def _field_hits(payloads: list[Any]) -> list[str]:
    hits = []

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if str(key) in DISALLOWED_REAL_ACCOUNT_FIELDS:
                    hits.append(str(key))
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    for payload in payloads:
        walk(payload)
    return hits


def _forbidden_artifacts(paths: ProjectPaths, as_of_date: str) -> dict[str, list[str]]:
    templates = {
        "buy_sell_signal_artifacts_present": [
            "outputs/equity_portfolio_tracking/daily/{date}/BUY_LIST.md",
            "outputs/equity_portfolio_tracking/daily/{date}/SELL_LIST.md",
            "data/equity_portfolio_tracking/daily/{date}/buy_list.json",
            "data/equity_portfolio_tracking/daily/{date}/sell_list.json",
        ],
        "order_preview_artifacts_present": [
            "outputs/equity_portfolio_tracking/daily/{date}/ORDER_PREVIEW.md",
            "data/equity_portfolio_tracking/daily/{date}/order_preview.json",
            "data/equity_portfolio_tracking/daily/{date}/orders.json",
        ],
        "broker_order_artifacts_present": [
            "data/equity_portfolio_tracking/daily/{date}/BROKER_ORDER.json",
            "data/equity_portfolio_tracking/daily/{date}/broker_order.json",
            "outputs/equity_portfolio_tracking/daily/{date}/BROKER_ORDER.md",
        ],
        "real_order_artifacts_present": [
            "data/equity_portfolio_tracking/daily/{date}/REAL_ORDER.json",
            "data/equity_portfolio_tracking/daily/{date}/real_order.json",
            "outputs/equity_portfolio_tracking/daily/{date}/REAL_ORDER.md",
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
    for path in artifacts.values():
        if not path.exists() or path.suffix not in {".json", ".md"}:
            continue
        text = path.read_text(encoding="utf-8").lower()
        for phrase in FORBIDDEN_POSITIVE_WORDING:
            if phrase.lower() in text:
                hits.append(f"{path.name}:{phrase}")
    return sorted(set(hits))


def _warnings(benchmark: dict[str, Any], summary: dict[str, Any]) -> list[str]:
    warnings = [str(item) for item in summary.get("warnings", []) if item]
    if benchmark and not benchmark.get("benchmark_data_available"):
        warnings.append(str(benchmark.get("benchmark_gap_reason") or "benchmark data unavailable"))
    return sorted(set(warnings))


def _load_any(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))
