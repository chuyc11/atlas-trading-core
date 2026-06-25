"""Shared package specs and helpers for authorized historical data acquisition."""

from __future__ import annotations

import csv
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from trading_core.storage.file_paths import ProjectPaths


START_DATE_DEFAULT = "2018-01-01"
RELEASE_CANDIDATE = "v0.5.7-authorized-full-historical-data-acquisition-audited"
PROXY_PACKAGE_ID = "GB-AUTHORIZED-FULL-HISTORICAL-PROXY-V1"
AUTHORIZED_GB_PACKAGE_ID = "HIST-AUTH-GLOBAL-BRIEFING-SIGNALS-V1"
ALLOWED_STATUSES = {
    "downloaded",
    "partial_downloaded",
    "loaded_from_local",
    "not_configured",
    "failed",
    "failed_soft",
    "skipped_optional",
    "normalized",
    "audit_passed",
    "audit_failed",
}
TRADING_AUTHORIZATION_NOTICE = "Historical data authorization is not trading authorization."
FORBIDDEN_DATA_WORDS = ["broker", "account", "order", "trade", "position", "margin"]


@dataclass(frozen=True)
class PackageSpec:
    package_id: str
    slug: str
    purpose: str
    required: bool
    critical: bool
    package_type: str
    source_priority: list[str]
    output_path: str
    report_path: str
    manifest_path: str


ETF_UNIVERSE = {
    "510300.SH": {"yahoo": "510300.SS", "currency": "CNY", "exchange": "SH"},
    "159915.SZ": {"yahoo": "159915.SZ", "currency": "CNY", "exchange": "SZ"},
    "588000.SH": {"yahoo": "588000.SS", "currency": "CNY", "exchange": "SH"},
    "512480.SH": {"yahoo": "512480.SS", "currency": "CNY", "exchange": "SH"},
    "512660.SH": {"yahoo": "512660.SS", "currency": "CNY", "exchange": "SH"},
    "512880.SH": {"yahoo": "512880.SS", "currency": "CNY", "exchange": "SH"},
    "2800.HK": {"yahoo": "2800.HK", "currency": "HKD", "exchange": "HK"},
    "3033.HK": {"yahoo": "3033.HK", "currency": "HKD", "exchange": "HK"},
}
BENCHMARK_UNIVERSE = {
    "CSI300": {"yahoo": "000300.SS"},
    "CSI500": {"yahoo": "000905.SS"},
    "CSI1000": {"yahoo": "000852.SS"},
    "CHINEXT": {"yahoo": "399006.SZ"},
    "HSI": {"yahoo": "^HSI"},
    "HSTECH": {"yahoo": "3033.HK"},
}
FRED_SERIES = {
    "HIST-FX-USDCNY-V1": {"DEXCHUS": "usd_cny"},
    "HIST-GLOBAL-RISK-VIX-V1": {"VIXCLS": "vix_close"},
    "HIST-RATES-LIQUIDITY-V1": {"DGS2": "US_2Y", "DGS10": "US_10Y", "DFF": "FED_FUNDS", "SOFR": "SOFR"},
    "HIST-COMMODITY-INFLATION-RISK-V1": {"DCOILWTICO": "WTI", "DCOILBRENTEU": "BRENT", "GOLDAMGBD228NLBM": "GOLD"},
    "HIST-POLICY-UNCERTAINTY-EPU-V1": {"USEPUINDXD": "US_EPU"},
}


PACKAGE_SPECS: dict[str, PackageSpec] = {
    "HIST-ETF-OHLCV-CN-HK-V1": PackageSpec(
        "HIST-ETF-OHLCV-CN-HK-V1",
        "hist_etf_ohlcv",
        "historical replay prices, isolated replay valuation, ETF coverage audit, benchmark comparison",
        True,
        True,
        "market_ohlcv",
        ["local_authorized_export", "yahoo_query_or_equivalent_authorized_market_data_source", "fixture"],
        "data/market/historical/authorized/HIST-ETF-OHLCV-CN-HK-V1.csv",
        "outputs/system/HIST_ETF_OHLCV_PACKAGE_REPORT.md",
        "data/system/hist_etf_ohlcv_manifest.json",
    ),
    "HIST-BENCHMARK-INDEX-CN-HK-V1": PackageSpec(
        "HIST-BENCHMARK-INDEX-CN-HK-V1",
        "hist_benchmark_index",
        "benchmark index comparison and cash benchmark",
        True,
        True,
        "benchmark_ohlcv",
        ["local_authorized_export", "yahoo_query_or_equivalent_authorized_market_data_source", "fixture"],
        "data/market/historical/authorized/HIST-BENCHMARK-INDEX-CN-HK-V1.csv",
        "outputs/system/HIST_BENCHMARK_INDEX_PACKAGE_REPORT.md",
        "data/system/hist_benchmark_index_manifest.json",
    ),
    "HIST-FX-USDCNY-V1": PackageSpec(
        "HIST-FX-USDCNY-V1",
        "hist_fx_usdcny",
        "USD/CNY daily risk input",
        True,
        True,
        "macro_series",
        ["local_authorized_export", "fred", "fixture"],
        "data/global_briefing/authorized/packages/HIST-FX-USDCNY-V1.csv",
        "outputs/system/HIST_FX_USDCNY_PACKAGE_REPORT.md",
        "data/system/hist_fx_usdcny_manifest.json",
    ),
    "HIST-GLOBAL-RISK-VIX-V1": PackageSpec(
        "HIST-GLOBAL-RISK-VIX-V1",
        "hist_global_risk_vix",
        "VIX global risk input",
        True,
        True,
        "macro_series",
        ["local_authorized_export", "fred", "cboe_vix", "fixture"],
        "data/global_briefing/authorized/packages/HIST-GLOBAL-RISK-VIX-V1.csv",
        "outputs/system/HIST_GLOBAL_RISK_VIX_PACKAGE_REPORT.md",
        "data/system/hist_global_risk_vix_manifest.json",
    ),
    "HIST-RATES-LIQUIDITY-V1": PackageSpec(
        "HIST-RATES-LIQUIDITY-V1",
        "hist_rates_liquidity",
        "rates and liquidity proxy input",
        True,
        False,
        "macro_series_long",
        ["local_authorized_export", "fred", "fixture"],
        "data/global_briefing/authorized/packages/HIST-RATES-LIQUIDITY-V1.csv",
        "outputs/system/HIST_RATES_LIQUIDITY_PACKAGE_REPORT.md",
        "data/system/hist_rates_liquidity_manifest.json",
    ),
    "HIST-COMMODITY-INFLATION-RISK-V1": PackageSpec(
        "HIST-COMMODITY-INFLATION-RISK-V1",
        "hist_commodity_inflation_risk",
        "commodity and inflation risk proxy input",
        True,
        False,
        "macro_series_long",
        ["local_authorized_export", "fred", "fixture"],
        "data/global_briefing/authorized/packages/HIST-COMMODITY-INFLATION-RISK-V1.csv",
        "outputs/system/HIST_COMMODITY_INFLATION_RISK_PACKAGE_REPORT.md",
        "data/system/hist_commodity_inflation_risk_manifest.json",
    ),
    "HIST-POLICY-UNCERTAINTY-EPU-V1": PackageSpec(
        "HIST-POLICY-UNCERTAINTY-EPU-V1",
        "hist_policy_uncertainty_epu",
        "policy uncertainty proxy input",
        True,
        False,
        "macro_series_long",
        ["local_authorized_export", "epu_authorized_api", "fred", "policy_uncertainty_public_file", "authorized_policy_uncertainty_proxy", "fixture"],
        "data/global_briefing/authorized/packages/HIST-POLICY-UNCERTAINTY-EPU-V1.csv",
        "outputs/system/HIST_POLICY_UNCERTAINTY_EPU_PACKAGE_REPORT.md",
        "data/system/hist_policy_uncertainty_epu_manifest.json",
    ),
    "HIST-OECD-CLI-MACRO-CYCLE-V1": PackageSpec(
        "HIST-OECD-CLI-MACRO-CYCLE-V1",
        "hist_oecd_cli_macro_cycle",
        "OECD CLI macro cycle proxy input",
        True,
        False,
        "oecd_cli",
        ["local_authorized_export", "oecd_authorized_api", "oecd_public_api", "authorized_macro_cycle_proxy", "fixture"],
        "data/global_briefing/authorized/packages/HIST-OECD-CLI-MACRO-CYCLE-V1.csv",
        "outputs/system/HIST_OECD_CLI_MACRO_CYCLE_PACKAGE_REPORT.md",
        "data/system/hist_oecd_cli_macro_cycle_manifest.json",
    ),
    AUTHORIZED_GB_PACKAGE_ID: PackageSpec(
        AUTHORIZED_GB_PACKAGE_ID,
        "hist_auth_global_briefing_signals",
        "optional authorized internal global-briefing historical signal package",
        False,
        False,
        "global_briefing_signal",
        ["GB_AUTH_PACKAGE_PATH", "gb_authorized_api", "local_authorized_export"],
        "data/global_briefing/authorized/packages/HIST-AUTH-GLOBAL-BRIEFING-SIGNALS-V1.raw",
        "outputs/system/HIST_AUTH_GLOBAL_BRIEFING_SIGNALS_PACKAGE_REPORT.md",
        "data/system/hist_auth_global_briefing_signals_manifest.json",
    ),
}
REQUIRED_PACKAGE_IDS = list(PACKAGE_SPECS)
CRITICAL_PACKAGE_IDS = ["HIST-ETF-OHLCV-CN-HK-V1", "HIST-BENCHMARK-INDEX-CN-HK-V1"]


def latest_end_date(end_date: str | None = None) -> str:
    if not end_date or end_date == "latest":
        return date.today().isoformat()
    return end_date


def project_path(paths: ProjectPaths, raw: str | Path) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else paths.project_root / path


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists() or not path.is_file():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def write_csv_rows(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})
    return path


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    return path


def package_dates(rows: list[dict[str, Any]], key: str = "date") -> tuple[str | None, str | None]:
    dates = sorted(str(row.get(key, "")) for row in rows if str(row.get(key, "")).strip())
    return (dates[0], dates[-1]) if dates else (None, None)


def coverage_ratio(date_min: str | None, date_max: str | None, start_date: str, end_date: str) -> float:
    if not date_min or not date_max:
        return 0.0
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    observed_start = max(start, date.fromisoformat(date_min))
    observed_end = min(end, date.fromisoformat(date_max))
    if observed_end < observed_start:
        return 0.0
    total = max(1, (end - start).days + 1)
    observed = (observed_end - observed_start).days + 1
    return round(observed / total, 6)


def source_host(url: str | None) -> str | None:
    if not url:
        return None
    return urlparse(url).netloc


def sanitize_url(url: str) -> str:
    parsed = urlparse(url)
    safe_query = urlencode([(key, "REDACTED") if _looks_secret(key) else (key, value) for key, value in parse_qsl(parsed.query, keep_blank_values=True)])
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, safe_query, ""))


def _looks_secret(key: str) -> bool:
    lowered = key.lower()
    return any(token in lowered for token in ["token", "key", "secret", "password", "auth"])


def secret_values() -> list[str]:
    values = []
    for key, value in os.environ.items():
        if value and _looks_secret(key):
            values.append(str(value))
    return values


def text_contains_secret(text: str) -> bool:
    return any(secret and secret in text for secret in secret_values())


def is_forbidden_data_package(package_id: str) -> bool:
    lowered = package_id.lower()
    return any(word in lowered for word in FORBIDDEN_DATA_WORDS)


def local_authorized_candidates(paths: ProjectPaths, package_id: str) -> list[Path]:
    root = paths.data_dir / "global_briefing" / "authorized" / "input"
    market_root = paths.data_dir / "market" / "historical" / "authorized" / "input"
    subdir_map = {
        "HIST-POLICY-UNCERTAINTY-EPU-V1": ["epu"],
        "HIST-OECD-CLI-MACRO-CYCLE-V1": ["oecd_cli"],
    }
    names = [package_id, package_id.lower(), package_id.replace("-", "_"), package_id.lower().replace("-", "_")]
    suffixes = [".csv", ".jsonl", ".json", ".raw"]
    direct = [base / f"{name}{suffix}" for base in [root, market_root] for name in names for suffix in suffixes]
    subdirs = []
    for name in subdir_map.get(package_id, []):
        directory = root / name
        if directory.exists():
            subdirs.extend(sorted(path for path in directory.glob("*") if path.suffix.lower() in suffixes))
    return [*direct, *subdirs]


def fixture_path(paths: ProjectPaths, name: str) -> Path:
    return paths.project_root / "tests" / "fixtures" / "historical_data" / name


def package_status_counts(packages: list[dict[str, Any]]) -> dict[str, int]:
    counts = {status: 0 for status in ["downloaded", "partial_downloaded", "loaded_from_local", "not_configured", "failed", "failed_soft", "skipped_optional", "normalized", "audit_passed", "audit_failed"]}
    for package in packages:
        status = str(package.get("status", "unknown"))
        counts[status] = counts.get(status, 0) + 1
    return counts


def package_report_markdown(title: str, payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"# {title}",
            "",
            "## Scope",
            TRADING_AUTHORIZATION_NOTICE,
            "This package is historical research data only.",
            "",
            "## Status",
            f"- package_id={payload.get('package_id')}",
            f"- status={payload.get('status')}",
            f"- source={payload.get('source')}",
            f"- row_count={payload.get('row_count')}",
            f"- date_min={payload.get('date_min')}",
            f"- date_max={payload.get('date_max')}",
            f"- coverage_ratio={payload.get('coverage_ratio')}",
            f"- sha256={payload.get('sha256')}",
            "",
            "## Warnings",
            *([f"- {item}" for item in payload.get("warnings", [])] if payload.get("warnings") else ["- none"]),
            "",
            "## Boundary",
            "- historical data download only",
            "- not trading authorization",
            "- no broker data",
            "- no account/order/trade/position/margin data",
            "- no main ledger write",
            "- no run-daily call",
            "",
        ]
    )
