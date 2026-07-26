"""Shared helpers for the v0.6.0 baseline strategy pack."""

from __future__ import annotations

import csv
from collections.abc import Iterable
from datetime import date, timedelta
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

from trading_core.execution.common import read_dict as read_dict, read_rows, rel, standard_boundary, write_rows
from trading_core.execution.trading_calendar_contract import default_calendar
from trading_core.storage.file_paths import ProjectPaths
from trading_core.storage.jsonl_store import write_json
from trading_core.system.common import default_paths


RELEASE_CANDIDATE = "v0.6.0-baseline-strategy-pack-audited"
BASELINE_FROM = "v0.5.9-ashare-execution-rules-hardened"
NEXT_VERSION = "v0.6.1-daily-workflow-binding"
RESEARCH_NOTICE = "Baseline strategy pack is research-only and does not start forward dry-run."
DEFAULT_START_DATE = "2024-01-02"
DEFAULT_END_DATE = "2024-12-31"
STRATEGY_IDS = [
    "equal_weight_etf_rotation",
    "momentum_risk_adjusted_rotation",
    "defensive_cash_rotation",
]
DEFAULT_UNIVERSE = [
    "510300.SH",
    "159915.SZ",
    "588000.SH",
    "512480.SH",
    "512660.SH",
    "512880.SH",
    "2800.HK",
    "3033.HK",
]
DEFAULT_BENCHMARKS = [
    "CSI300",
    "CSI500",
    "CSI1000",
    "CHINEXT",
    "HSI",
    "HSTECH",
    "CASH",
    "EQUAL_ETF",
]
PRICE_PACKAGE = Path("data/market/historical/authorized/HIST-ETF-OHLCV-CN-HK-V1.csv")
RISK_PACKAGE = Path("data/global_briefing/normalized/GB-AUTHORIZED-FULL-HISTORICAL-PROXY-V1.normalized.jsonl")


def paths_or_default(paths: ProjectPaths | None = None) -> ProjectPaths:
    return default_paths(paths)


def selected_strategies(strategy: str | None) -> list[str]:
    if not strategy or strategy == "all":
        return list(STRATEGY_IDS)
    if strategy not in STRATEGY_IDS:
        raise ValueError(f"Unsupported baseline strategy: {strategy}")
    return [strategy]


def date_range(start_date: str, end_date: str) -> list[str]:
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    if end < start:
        return []
    output = []
    current = start
    while current <= end:
        output.append(current.isoformat())
        current += timedelta(days=1)
    return output


def lookback_start(start_date: str, days: int = 120) -> str:
    return (date.fromisoformat(start_date) - timedelta(days=days)).isoformat()


def trading_dates(start_date: str, end_date: str) -> list[str]:
    calendar = default_calendar()
    return [day for day in date_range(start_date, end_date) if calendar.is_trading_day(day, "SSE")]


def market_for_symbol(symbol: str) -> str:
    return default_calendar().market_for_symbol(symbol)


def next_execution_date(signal_date: str) -> str:
    return default_calendar().next_trading_day(signal_date, "SSE")


def strategy_version(strategy_id: str) -> str:
    return f"{strategy_id}_v1"


def strategy_slug(strategy_id: str, start_date: str, end_date: str) -> str:
    return f"{strategy_id}-{start_date}-{end_date}"


def signal_path(paths: ProjectPaths, strategy_id: str, start_date: str, end_date: str) -> Path:
    return paths.data_dir / "strategies" / "signals" / f"baseline_signals-{strategy_slug(strategy_id, start_date, end_date)}.jsonl"


def signal_report_path(paths: ProjectPaths, strategy_id: str, start_date: str, end_date: str) -> Path:
    return paths.outputs_dir / "strategies" / f"BASELINE_SIGNALS-{strategy_slug(strategy_id, start_date, end_date)}.md"


def preview_path(paths: ProjectPaths, strategy_id: str, start_date: str, end_date: str) -> Path:
    return paths.data_dir / "strategies" / "order_previews" / f"order_preview-{strategy_slug(strategy_id, start_date, end_date)}.jsonl"


def preview_report_path(paths: ProjectPaths, strategy_id: str, start_date: str, end_date: str) -> Path:
    return paths.outputs_dir / "strategies" / f"ORDER_PREVIEW-{strategy_slug(strategy_id, start_date, end_date)}.md"


def replay_root(paths: ProjectPaths, strategy_id: str) -> Path:
    return paths.data_dir / "replays" / "strategies" / strategy_id


def replay_summary_path(paths: ProjectPaths, strategy_id: str, start_date: str, end_date: str) -> Path:
    return replay_root(paths, strategy_id) / f"replay-{start_date}-{end_date}.json"


def replay_report_path(paths: ProjectPaths, strategy_id: str, start_date: str, end_date: str) -> Path:
    return paths.outputs_dir / "replays" / "strategies" / strategy_id / f"REPLAY-{start_date}-{end_date}.md"


def benchmark_path(paths: ProjectPaths, start_date: str, end_date: str) -> Path:
    return paths.data_dir / "strategies" / "benchmark_comparison" / f"baseline_benchmark_comparison-{start_date}-{end_date}.json"


def benchmark_report_path(paths: ProjectPaths, start_date: str, end_date: str) -> Path:
    return paths.outputs_dir / "strategies" / f"BASELINE_BENCHMARK_COMPARISON-{start_date}-{end_date}.md"


def report_path(paths: ProjectPaths, strategy_id: str, start_date: str, end_date: str) -> Path:
    return paths.data_dir / "strategies" / "reports" / f"baseline_strategy_report-{strategy_slug(strategy_id, start_date, end_date)}.json"


def report_markdown_path(paths: ProjectPaths, strategy_id: str, start_date: str, end_date: str) -> Path:
    return paths.outputs_dir / "strategies" / f"BASELINE_STRATEGY_REPORT-{strategy_slug(strategy_id, start_date, end_date)}.md"


def latest_signal_file(paths: ProjectPaths, strategy_id: str) -> Path | None:
    root = paths.data_dir / "strategies" / "signals"
    matches = sorted(root.glob(f"baseline_signals-{strategy_id}-*.jsonl")) if root.exists() else []
    return matches[-1] if matches else None


def parse_dates_from_signal_file(path: Path, strategy_id: str) -> tuple[str, str]:
    stem = path.stem.removeprefix(f"baseline_signals-{strategy_id}-")
    return stem[:10], stem[11:21]


def load_price_history(paths: ProjectPaths, *, start_date: str, end_date: str) -> tuple[dict[str, dict[str, float]], dict[str, Any]]:
    source_path = paths.project_root / PRICE_PACKAGE
    rows: dict[str, dict[str, float]] = {}
    if source_path.exists():
        with source_path.open("r", encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                symbol = row.get("symbol", "")
                day = row.get("date", "")
                if symbol not in DEFAULT_UNIVERSE or not day or day > end_date:
                    continue
                if day < lookback_start(start_date):
                    continue
                raw_price = row.get("adjusted_close") or row.get("close") or "0"
                try:
                    price = float(raw_price)
                except ValueError:
                    continue
                if price <= 0:
                    continue
                rows.setdefault(day, {})[symbol] = price
        if rows:
            return rows, {"source": rel(source_path, paths), "fallback_used": False}
    return _synthetic_prices(start_date, end_date), {"source": "deterministic_fixture_fallback", "fallback_used": True}


def _synthetic_prices(start_date: str, end_date: str) -> dict[str, dict[str, float]]:
    output: dict[str, dict[str, float]] = {}
    for index, day in enumerate(trading_dates(lookback_start(start_date), end_date)):
        output[day] = {}
        for symbol_index, symbol in enumerate(DEFAULT_UNIVERSE):
            drift = 0.0015 * ((symbol_index % 3) - 1)
            cycle = ((index + symbol_index) % 17 - 8) * 0.002
            output[day][symbol] = round(2.0 + symbol_index * 0.7 + index * drift + cycle, 6)
    return output


def load_risk_history(paths: ProjectPaths, *, start_date: str, end_date: str) -> tuple[dict[str, float], dict[str, Any]]:
    source_path = paths.project_root / RISK_PACKAGE
    risks: dict[str, float] = {}
    if source_path.exists():
        for row in read_rows(source_path):
            day = str(row.get("as_of_date") or row.get("date") or "")
            if not day or day < lookback_start(start_date, 10) or day > end_date:
                continue
            signals = row.get("signals", {})
            if not isinstance(signals, dict):
                continue
            value = signals.get("global_risk_off", signals.get("risk_off"))
            if isinstance(value, int | float):
                risks[day] = float(value)
        if risks:
            return risks, {"source": rel(source_path, paths), "fallback_used": False}
    for index, day in enumerate(trading_dates(lookback_start(start_date, 10), end_date)):
        risks[day] = round(0.35 + (0.35 if index % 13 == 0 else 0.0) + (index % 5) * 0.02, 6)
    return risks, {"source": "deterministic_fixture_fallback", "fallback_used": True}


def latest_on_or_before(series: dict[str, Any], day: str) -> tuple[str | None, Any | None]:
    candidates = [candidate for candidate in series if candidate <= day]
    if not candidates:
        return None, None
    selected = max(candidates)
    return selected, series[selected]


def price_on_or_before(prices: dict[str, dict[str, float]], symbol: str, day: str) -> tuple[str | None, float | None]:
    for candidate in sorted((item for item in prices if item <= day), reverse=True):
        value = prices.get(candidate, {}).get(symbol)
        if value is not None:
            return candidate, value
    return None, None


def returns_for_symbol(prices: dict[str, dict[str, float]], symbol: str, day: str, lookback: int) -> list[float]:
    available = sorted(candidate for candidate in prices if candidate <= day and symbol in prices[candidate])
    if len(available) < 2:
        return []
    window = available[-(lookback + 1) :]
    returns = []
    for previous, current in zip(window, window[1:], strict=False):
        prev_price = prices[previous][symbol]
        current_price = prices[current][symbol]
        if prev_price > 0:
            returns.append(current_price / prev_price - 1.0)
    return returns


def trailing_return(prices: dict[str, dict[str, float]], symbol: str, day: str, lookback: int) -> float | None:
    available = sorted(candidate for candidate in prices if candidate <= day and symbol in prices[candidate])
    if len(available) <= lookback:
        return None
    start = available[-(lookback + 1)]
    end = available[-1]
    start_price = prices[start][symbol]
    end_price = prices[end][symbol]
    return end_price / start_price - 1.0 if start_price > 0 else None


def annualized_return(cumulative_return: float, days: int) -> float:
    if days <= 0:
        return 0.0
    return (1.0 + cumulative_return) ** (252 / days) - 1.0


def annualized_volatility(returns: Iterable[float]) -> float:
    values = list(returns)
    if len(values) < 2:
        return 0.0
    return pstdev(values) * (252**0.5)


def max_drawdown(values: list[float]) -> float:
    if not values:
        return 0.0
    peak = values[0]
    drawdown = 0.0
    for value in values:
        peak = max(peak, value)
        if peak:
            drawdown = min(drawdown, value / peak - 1.0)
    return drawdown


def mean_return(returns: Iterable[float]) -> float:
    values = list(returns)
    return mean(values) if values else 0.0


def simulated_price_status(symbol: str, execution_date: str) -> str:
    if symbol == "588000.SH" and execution_date in {"2024-01-03", "2024-01-04"}:
        return "suspended"
    return "tradable"


def write_json_artifact(path: Path, payload: dict[str, Any]) -> str:
    write_json(path, payload)
    return str(path)


def rows_and_paths(path: Path, rows: list[dict[str, Any]]) -> str:
    write_rows(path, rows)
    return str(path)


def research_boundary(scope_key: str) -> dict[str, Any]:
    boundary = standard_boundary(scope_key)
    boundary.update(
        {
            "baseline_strategy_pack_only": scope_key == "baseline_strategy_pack_only",
            "ml_trading_approved": False,
            "llm_trading_approved": False,
            "rl_trading_approved": False,
        }
    )
    return boundary


def markdown_boundary(scope: str) -> list[str]:
    return [
        f"- {scope}",
        "- run-daily not called",
        "- forward dry-run not started",
        "- main ledger not written",
        "- ML shadow not used as authorization",
        "- LLM not used for trading decision",
        "- RL not used",
        "- promotion not triggered",
    ]
