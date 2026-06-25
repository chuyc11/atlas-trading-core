"""Build global-briefing-compatible proxy signals from historical packages."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from trading_core.global_briefing.historical_data_packages import PROXY_PACKAGE_ID, read_csv_rows, write_jsonl
from trading_core.global_briefing.signal_package_validator import validate_global_briefing_signals
from trading_core.storage.file_paths import ProjectPaths


def build_full_historical_proxy_package(
    *,
    package_paths: dict[str, str],
    start_date: str,
    end_date: str,
    paths: ProjectPaths,
) -> dict[str, Any]:
    warnings: list[str] = []
    etf_rows = read_csv_rows(Path(package_paths.get("HIST-ETF-OHLCV-CN-HK-V1", "")))
    dates = sorted({row["date"] for row in etf_rows if start_date <= row.get("date", "") <= end_date and row.get("symbol") == "510300.SH"})
    if not dates:
        warnings.append("missing critical ETF price dates for proxy construction")
    fx = _series_by_date(Path(package_paths.get("HIST-FX-USDCNY-V1", "")), "usd_cny")
    vix = _series_by_date(Path(package_paths.get("HIST-GLOBAL-RISK-VIX-V1", "")), "vix_close")
    rates = _long_series(Path(package_paths.get("HIST-RATES-LIQUIDITY-V1", "")))
    commodities = _long_series(Path(package_paths.get("HIST-COMMODITY-INFLATION-RISK-V1", "")))
    epu = _long_series(Path(package_paths.get("HIST-POLICY-UNCERTAINTY-EPU-V1", "")))
    oecd = _oecd_series(Path(package_paths.get("HIST-OECD-CLI-MACRO-CYCLE-V1", "")))
    if not fx:
        warnings.append("missing critical USD/CNY package for proxy; fx_pressure will be null")
    if not vix:
        warnings.append("missing critical VIX package for proxy; market_stress will be null")
    if not rates:
        warnings.append("missing optional rates/liquidity package; liquidity_pressure and rates_pressure may be null")
    if not commodities:
        warnings.append("missing optional commodity package; commodity_inflation_pressure may be null")
    if not epu:
        warnings.append("missing optional EPU package; policy_uncertainty may be null")
    if not oecd:
        warnings.append("missing optional OECD CLI package; macro_cycle_pressure may be null")

    rows = []
    for day in dates:
        vix_value = _latest(vix, day)
        fx_value = _latest(fx, day)
        us10y = _latest(rates.get("US_10Y", {}), day)
        us2y = _latest(rates.get("US_2Y", {}), day)
        wti = _latest(commodities.get("WTI", {}), day)
        epu_value = _latest(epu.get("US_EPU", {}), day)
        cli_value = _latest(oecd.get("CHINA", {}), day)
        market_stress = _clip(((vix_value or 15.0) - 15.0) / 25.0) if vix_value is not None else None
        fx_pressure = _clip(((fx_value or 6.5) - 6.5) / 1.2) if fx_value is not None else None
        rates_pressure = _clip(((us10y or 3.0) - 2.0) / 4.0) if us10y is not None else None
        liquidity_pressure = _clip(((us2y or 3.0) - 2.0) / 4.0) if us2y is not None else None
        commodity_pressure = _clip(((wti or 70.0) - 60.0) / 70.0) if wti is not None else None
        policy_uncertainty = _clip((epu_value or 100.0) / 500.0) if epu_value is not None else None
        macro_cycle_pressure = _clip((100.0 - (cli_value or 100.0)) / 10.0) if cli_value is not None else None
        risk_components = [value for value in [market_stress, fx_pressure, rates_pressure, commodity_pressure, policy_uncertainty, macro_cycle_pressure] if value is not None]
        global_risk_off = round(sum(risk_components) / len(risk_components), 6) if risk_components else None
        risk_on = round(1.0 - global_risk_off, 6) if global_risk_off is not None else 0.0
        policy_support = round(_clip(1.0 - (policy_uncertainty or 0.0)), 6) if policy_uncertainty is not None else 0.0
        liquidity = round(_clip(1.0 - (liquidity_pressure or 0.0)), 6) if liquidity_pressure is not None else 0.0
        rows.append(
            {
                "as_of_date": day,
                "generated_at": f"{day}T00:00:00Z",
                "region": "CN_GLOBAL",
                "signals": {
                    "vix": vix_value,
                    "usd_cny": fx_value,
                    "market_stress": market_stress,
                    "fx_pressure": fx_pressure,
                    "liquidity_pressure": liquidity_pressure,
                    "rates_pressure": rates_pressure,
                    "commodity_inflation_pressure": commodity_pressure,
                    "policy_uncertainty": policy_uncertainty,
                    "macro_cycle_pressure": macro_cycle_pressure,
                    "global_risk_off": global_risk_off,
                    "risk_on": risk_on,
                    "liquidity": liquidity,
                    "policy_support": policy_support,
                },
                "source": "authorized_full_historical_proxy",
                "version": "v0.5.7_proxy_v1",
            }
        )
    package_path = paths.data_dir / "global_briefing" / "authorized" / "packages" / f"{PROXY_PACKAGE_ID}.jsonl"
    normalized_path = paths.data_dir / "global_briefing" / "normalized" / f"{PROXY_PACKAGE_ID}.normalized.jsonl"
    write_jsonl(package_path, rows)
    write_jsonl(normalized_path, rows)
    validation = validate_global_briefing_signals(str(normalized_path), start_date=start_date, end_date=end_date, paths=paths)
    manifest = {
        "package_id": PROXY_PACKAGE_ID,
        "status": "built",
        "validated": validation["overall_passed"],
        "row_count": len(rows),
        "date_min": rows[0]["as_of_date"] if rows else None,
        "date_max": rows[-1]["as_of_date"] if rows else None,
        "package_path": str(package_path),
        "normalized_path": str(normalized_path),
        "validation_path": validation["json_path"],
        "warnings": warnings + validation["warnings"],
        "blocking_reasons": validation["blocking_reasons"],
        "boundary": {
            "proxy_package_only": True,
            "proxy_signals_not_internal_global_briefing": True,
            "main_ledger_written": False,
            "run_daily_called": False,
            "future_signal_used": False,
        },
    }
    manifest_path = paths.data_dir / "system" / "authorized_full_historical_proxy_manifest.json"
    report_path = paths.outputs_dir / "system" / "AUTHORIZED_FULL_HISTORICAL_PROXY_PACKAGE_REPORT.md"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    report_path.write_text(build_proxy_markdown(manifest), encoding="utf-8")
    return {**manifest, "manifest_path": str(manifest_path), "report_path": str(report_path)}


def _series_by_date(path: Path, column: str) -> dict[str, float]:
    output = {}
    for row in read_csv_rows(path):
        value = _float(row.get(column))
        if value is not None:
            output[str(row.get("date"))] = value
    return output


def _long_series(path: Path) -> dict[str, dict[str, float]]:
    output: dict[str, dict[str, float]] = {}
    for row in read_csv_rows(path):
        value = _float(row.get("value"))
        series_id = str(row.get("series_id", ""))
        if value is not None and series_id:
            output.setdefault(series_id, {})[str(row.get("date"))] = value
    return output


def _oecd_series(path: Path) -> dict[str, dict[str, float]]:
    output: dict[str, dict[str, float]] = {}
    for row in read_csv_rows(path):
        value = _float(row.get("cli_value"))
        region = str(row.get("region", "")).upper()
        if value is not None and region:
            output.setdefault(region, {})[str(row.get("date"))] = value
    return output


def _latest(series: dict[str, float], day: str) -> float | None:
    candidates = [date for date in series if date <= day]
    if not candidates:
        return None
    return series[max(candidates)]


def _float(value: Any) -> float | None:
    try:
        if value in (None, "", "."):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _clip(value: float) -> float:
    return round(max(0.0, min(1.0, float(value))), 6)


def build_proxy_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Authorized Full Historical Proxy Package Report",
            "",
            "## Scope",
            "This is a global-briefing-compatible proxy package.",
            "It is not an internal global-briefing signal package.",
            "Historical data authorization is not trading authorization.",
            "",
            "## Status",
            f"- status={payload['status']}",
            f"- validated={str(payload['validated']).lower()}",
            f"- row_count={payload['row_count']}",
            f"- date_min={payload['date_min']}",
            f"- date_max={payload['date_max']}",
            "",
            "## Boundary",
            "- proxy signals are not internal global-briefing signals",
            "- no future signal used",
            "- no main ledger write",
            "- no run-daily call",
            "- not forward dry-run validation",
            "- not strategy effectiveness proof",
            "",
        ]
    )
