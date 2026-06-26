"""Shared helpers for v0.6.3 virtual forward dry-run day 1."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

from trading_core.daily_workflow.common import (
    BENCHMARK_DATA_SOURCE,
    MARKET_DATA_SOURCE,
    RISK_PROXY_SOURCE,
    benchmark_rows_for_date,
    latest_available_market_date,
    market_rows_for_date,
    price_for_symbol,
    risk_proxy_for_date,
    sha256_file,
    volume_for_symbol,
)
from trading_core.execution.common import read_dict, rel
from trading_core.execution.trading_calendar_contract import default_calendar
from trading_core.storage.file_paths import ProjectPaths
from trading_core.strategies.common import DEFAULT_BENCHMARKS, DEFAULT_UNIVERSE
from trading_core.system.common import default_paths, write_json_markdown


RELEASE_CANDIDATE = "v0.6.3-forward-dry-run-day1-executed-audited"
NEXT_VERSION = "v0.6.4-forward-dry-run-day2-continuation"
DAY_INDEX = 1
DAY_LABEL = "day_001"
INITIAL_CASH_PER_STRATEGY = 1_000_000.0
NOTICE = "This is virtual forward dry-run only. This is not real trading."


def paths_or_default(paths: ProjectPaths | None = None) -> ProjectPaths:
    return default_paths(paths)


def day_root(paths: ProjectPaths) -> Path:
    return paths.data_dir / "forward_dry_run" / DAY_LABEL


def day_output_root(paths: ProjectPaths) -> Path:
    return paths.outputs_dir / "forward_dry_run" / DAY_LABEL


def ledger_root(paths: ProjectPaths) -> Path:
    return paths.data_dir / "forward_dry_run" / "ledger"


def ledger_output_root(paths: ProjectPaths) -> Path:
    return paths.outputs_dir / "forward_dry_run" / "ledger"


def day_json(paths: ProjectPaths, filename: str) -> Path:
    return day_root(paths) / filename


def day_report(paths: ProjectPaths, filename: str) -> Path:
    return day_output_root(paths) / filename


def system_json(paths: ProjectPaths, filename: str) -> Path:
    return paths.data_dir / "system" / filename


def system_report(paths: ProjectPaths, filename: str) -> Path:
    return paths.outputs_dir / "system" / filename


def audit_report(paths: ProjectPaths, filename: str) -> Path:
    return paths.outputs_dir / "audit" / filename


def read_json_file(path: Path) -> dict[str, Any]:
    return read_dict(path)


def read_system(paths: ProjectPaths, filename: str) -> dict[str, Any]:
    return read_json_file(system_json(paths, filename))


def write_artifact(json_path: Path, payload: dict[str, Any], report_path: Path, markdown: str) -> dict[str, Any]:
    write_json_markdown(json_path, payload, report_path, markdown)
    return {**payload, "json_path": str(json_path), "report_path": str(report_path)}


def write_json_only(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def boundary(scope_key: str) -> dict[str, Any]:
    return {
        scope_key: True,
        "virtual_forward_dry_run_only": True,
        "real_trading": False,
        "broker_connected": False,
        "real_orders_placed": False,
        "real_orders_enabled": False,
        "broker_execution": False,
        "main_ledger_written": False,
        "main_orders_written": False,
        "main_trades_written": False,
        "main_portfolio_written": False,
        "main_accounts_written": False,
        "ml_shadow_used_as_authorization": False,
        "llm_trading_decision": False,
        "rl_used": False,
        "promotion_triggered": False,
        "strategy_effectiveness_proven": False,
        "forward_dry_run_fully_validated": False,
        "live_trading_ready": False,
    }


def non_claim_lines() -> list[str]:
    return [
        "- This is virtual forward dry-run only.",
        "- This is not real trading.",
        "- This is not strategy effectiveness proof.",
        "- This is not forward dry-run validation completion.",
        "- This is not live trading readiness.",
        "- No broker is connected.",
        "- No real orders were placed.",
        "- ML/LLM/RL did not make trading decisions.",
        "- No strategy promotion was triggered.",
    ]


def no_broker_live_config() -> bool:
    enabled_keys = {
        "BROKER_CONNECTED",
        "BROKER_ENABLED",
        "BROKER_ORDER_ENABLED",
        "LIVE_TRADING",
        "LIVE_TRADING_ENABLED",
        "REAL_TRADING_ENABLED",
        "ALPACA_LIVE_TRADING_ENABLED",
        "IBKR_LIVE_TRADING_ENABLED",
    }
    enabled_values = {"1", "true", "yes", "on", "enabled"}
    return not any(os.environ.get(key, "").strip().lower() in enabled_values for key in enabled_keys)


def git_status_clean(paths: ProjectPaths) -> bool:
    if not (paths.project_root / ".git").exists():
        return True
    try:
        result = subprocess.run(["git", "status", "--short"], cwd=paths.project_root, check=False, capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return False
    return result.stdout.strip() == ""


def day1_already_executed(paths: ProjectPaths) -> bool:
    result = day_json(paths, "day1_virtual_execution_result.json")
    if not result.exists():
        return False
    payload = read_json_file(result)
    return payload.get("executed") is True


def eligible_as_of_date(paths: ProjectPaths, as_of_date: str | None = None) -> tuple[str, dict[str, Any]]:
    selected = as_of_date or latest_available_market_date(paths) or ""
    market_rows = market_rows_for_date(paths, selected)
    benchmark_rows = benchmark_rows_for_date(paths, selected)
    risk_row = risk_proxy_for_date(paths, selected)
    missing_symbols = [symbol for symbol in DEFAULT_UNIVERSE if symbol not in market_rows or price_for_symbol(market_rows, symbol) is None or volume_for_symbol(market_rows, symbol) is None]
    missing_benchmarks = [benchmark for benchmark in DEFAULT_BENCHMARKS if benchmark != "EQUAL_ETF" and benchmark not in benchmark_rows]
    calendar = default_calendar()
    details = {
        "as_of_date": selected,
        "universe_complete": not missing_symbols,
        "missing_symbols": missing_symbols,
        "benchmark_complete": not missing_benchmarks,
        "missing_benchmarks": missing_benchmarks,
        "risk_proxy_complete": risk_row is not None,
        "trading_calendar_passed": bool(selected) and calendar.is_trading_day(selected, "SSE"),
        "latest_available_trading_date": latest_available_market_date(paths),
    }
    details["eligible"] = bool(selected) and details["universe_complete"] and details["benchmark_complete"] and details["risk_proxy_complete"] and details["trading_calendar_passed"]
    return selected, details


def source_hashes(paths: ProjectPaths) -> dict[str, dict[str, Any]]:
    sources = {
        "market_data": MARKET_DATA_SOURCE,
        "benchmark_data": BENCHMARK_DATA_SOURCE,
        "risk_proxy": RISK_PROXY_SOURCE,
    }
    output = {}
    for key, relative in sources.items():
        path = paths.project_root / relative
        output[key] = {"path": relative.as_posix(), "exists": path.exists(), "sha256": sha256_file(path)}
    return output


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
