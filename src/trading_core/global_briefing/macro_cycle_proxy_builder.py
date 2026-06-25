"""Build a PIT-safe macro-cycle proxy when official OECD CLI is unavailable."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from trading_core.global_briefing.historical_data_packages import read_csv_rows
from trading_core.storage.file_paths import ProjectPaths


REGIONS = ["CN", "US", "OECD_TOTAL", "G20", "JP", "EURO_AREA"]


def build_macro_cycle_proxy_rows(paths: ProjectPaths, start_date: str, end_date: str) -> tuple[list[dict[str, Any]], list[str]]:
    warnings: list[str] = []
    benchmark = _benchmark_closes(paths)
    rates = _long_series(paths.data_dir / "global_briefing" / "authorized" / "packages" / "HIST-RATES-LIQUIDITY-V1.csv")
    commodities = _long_series(paths.data_dir / "global_briefing" / "authorized" / "packages" / "HIST-COMMODITY-INFLATION-RISK-V1.csv")
    fx = _simple_series(paths.data_dir / "global_briefing" / "authorized" / "packages" / "HIST-FX-USDCNY-V1.csv", "usd_cny")
    vix = _simple_series(paths.data_dir / "global_briefing" / "authorized" / "packages" / "HIST-GLOBAL-RISK-VIX-V1.csv", "vix_close")
    dates = sorted(day for day in benchmark if start_date <= day <= end_date)
    if not dates:
        warnings.append("macro-cycle proxy unavailable because benchmark package is missing")
        return [], warnings
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    rows: list[dict[str, Any]] = []
    for index, day in enumerate(dates):
        current = benchmark[day]
        lookback_index = max(0, index - 21)
        previous = benchmark[dates[lookback_index]]
        momentum = (current / previous - 1.0) if previous else 0.0
        us10y = _latest(rates.get("US_10Y") or rates.get("US_10Y_YAHOO_TNX") or {}, day)
        wti = _latest(commodities.get("WTI") or commodities.get("WTI_YAHOO_CL_F") or {}, day)
        fx_value = _latest(fx, day)
        vix_value = _latest(vix, day)
        rates_pressure = _clip(((us10y or 3.0) - 2.0) / 4.0)
        commodity_pressure = _clip(((wti or 70.0) - 60.0) / 70.0)
        fx_pressure = _clip(((fx_value or 6.5) - 6.5) / 1.2)
        market_stress = _clip(((vix_value or 15.0) - 15.0) / 25.0)
        cycle_pressure = _clip((market_stress * 0.35) + (rates_pressure * 0.20) + (commodity_pressure * 0.15) + (fx_pressure * 0.15) + (max(0.0, -momentum) * 3.0 * 0.15))
        cli_value = round(100.0 - (cycle_pressure * 10.0), 6)
        for region in REGIONS:
            rows.append(
                {
                    "date": day,
                    "region": region,
                    "cli_value": cli_value,
                    "macro_cycle_pressure": round(cycle_pressure, 6),
                    "source": "authorized_macro_cycle_proxy",
                    "official_oecd_cli": "false",
                    "macro_cycle_proxy": "true",
                    "downloaded_at": now,
                }
            )
    warnings.append("official OECD CLI unavailable; built authorized macro-cycle proxy from historical benchmark and macro packages.")
    return rows, warnings


def _benchmark_closes(paths: ProjectPaths) -> dict[str, float]:
    path = paths.data_dir / "market" / "historical" / "authorized" / "HIST-BENCHMARK-INDEX-CN-HK-V1.csv"
    rows = {}
    for row in read_csv_rows(path):
        if row.get("benchmark_id") != "CSI300":
            continue
        try:
            rows[str(row["date"])] = float(row["close"])
        except (KeyError, TypeError, ValueError):
            continue
    return rows


def _long_series(path) -> dict[str, dict[str, float]]:
    output: dict[str, dict[str, float]] = {}
    for row in read_csv_rows(path):
        try:
            output.setdefault(str(row.get("series_id")), {})[str(row.get("date"))] = float(row["value"])
        except (KeyError, TypeError, ValueError):
            continue
    return output


def _simple_series(path, column: str) -> dict[str, float]:
    output = {}
    for row in read_csv_rows(path):
        try:
            output[str(row.get("date"))] = float(row[column])
        except (KeyError, TypeError, ValueError):
            continue
    return output


def _latest(series: dict[str, float], day: str) -> float | None:
    candidates = [date for date in series if date <= day]
    return series[max(candidates)] if candidates else None


def _clip(value: float) -> float:
    return max(0.0, min(1.0, float(value)))
