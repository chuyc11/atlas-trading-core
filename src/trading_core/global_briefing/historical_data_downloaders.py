"""Download or load authorized historical data packages."""

from __future__ import annotations

import csv
import json
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from trading_core.global_briefing.historical_data_packages import (
    AUTHORIZED_GB_PACKAGE_ID,
    BENCHMARK_UNIVERSE,
    ETF_UNIVERSE,
    FRED_SERIES,
    PACKAGE_SPECS,
    PROXY_PACKAGE_ID,
    REQUIRED_PACKAGE_IDS,
    TRADING_AUTHORIZATION_NOTICE,
    coverage_ratio,
    fixture_path,
    latest_end_date,
    local_authorized_candidates,
    package_dates,
    package_report_markdown,
    package_status_counts,
    project_path,
    sanitize_url,
    sha256_file,
    source_host,
    write_csv_rows,
)
from trading_core.global_briefing.historical_data_source_resolver import resolve_historical_data_sources
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, timestamp_id, write_json_markdown


HttpGet = Callable[[str, int], bytes]


def download_historical_data_packages(
    *,
    packages: list[str] | None = None,
    start_date: str = "2018-01-01",
    end_date: str = "latest",
    continue_on_error: bool = False,
    source_mode: str = "auto",
    timeout_seconds: int = 8,
    max_retries: int = 1,
    paths: ProjectPaths | None = None,
    http_get: HttpGet | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    resolved_end_date = latest_end_date(end_date)
    package_ids = _parse_packages(packages)
    manifest_id, created_at = timestamp_id("HIST-DATA-DOWNLOAD-MANIFEST")
    resolution = resolve_historical_data_sources(packages=package_ids, start_date=start_date, end_date=resolved_end_date, paths=paths)
    resolution_by_id = {row["package_id"]: row for row in resolution["packages"]}
    downloader = http_get or _default_http_get
    results: list[dict[str, Any]] = []
    for package_id in package_ids:
        try:
            result = _download_one(
                package_id,
                start_date=start_date,
                end_date=resolved_end_date,
                source_mode=source_mode,
                timeout_seconds=timeout_seconds,
                max_retries=max_retries,
                paths=paths,
                http_get=downloader,
                resolution=resolution_by_id.get(package_id, {}),
            )
        except Exception as exc:  # noqa: BLE001 - package acquisition is fail-soft.
            if not continue_on_error:
                raise
            result = _failed_package(package_id, str(exc), paths, start_date, resolved_end_date)
        results.append(result)
    payload: dict[str, Any] = {
        "manifest_id": manifest_id,
        "created_at": created_at,
        "start_date": start_date,
        "end_date": resolved_end_date,
        "source_resolution": resolution["json_path"],
        "packages": results,
        "summary": {
            "required_packages": len(package_ids),
            **package_status_counts(results),
        },
        "boundary": {
            "historical_data_download_only": True,
            "trading_authorization": False,
            "main_ledger_written": False,
            "run_daily_called": False,
            "forward_dry_run_started": False,
            "broker_connected": False,
            "labels_used": False,
            "ml_shadow_used": False,
            "experiments_used": False,
            "promotion_triggered": False,
        },
    }
    json_path = paths.data_dir / "system" / "historical_data_download_manifest.json"
    md_path = paths.outputs_dir / "system" / "HISTORICAL_DATA_DOWNLOAD_MANIFEST.md"
    write_json_markdown(json_path, payload, md_path, build_download_manifest_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def _parse_packages(packages: list[str] | None) -> list[str]:
    if not packages:
        return list(REQUIRED_PACKAGE_IDS)
    output: list[str] = []
    for item in packages:
        output.extend(part.strip() for part in item.split(",") if part.strip())
    return output


def _download_one(
    package_id: str,
    *,
    start_date: str,
    end_date: str,
    source_mode: str,
    timeout_seconds: int,
    max_retries: int,
    paths: ProjectPaths,
    http_get: HttpGet,
    resolution: dict[str, Any],
) -> dict[str, Any]:
    spec = PACKAGE_SPECS[package_id]
    warnings: list[str] = []
    local_file = next((path for path in local_authorized_candidates(paths, package_id) if path.exists()), None)
    if local_file is not None:
        result = _load_local_package(package_id, local_file, paths, start_date, end_date)
    elif source_mode == "fixture":
        result = _load_fixture_package(package_id, paths, start_date, end_date)
    elif package_id == AUTHORIZED_GB_PACKAGE_ID:
        result = _authorized_gb_not_configured(paths, start_date, end_date)
    elif package_id == "HIST-ETF-OHLCV-CN-HK-V1":
        result = _download_etf_package(paths, start_date, end_date, timeout_seconds, max_retries, http_get)
    elif package_id == "HIST-BENCHMARK-INDEX-CN-HK-V1":
        result = _download_benchmark_package(paths, start_date, end_date, timeout_seconds, max_retries, http_get)
    elif package_id in FRED_SERIES:
        result = _download_fred_package(package_id, paths, start_date, end_date, timeout_seconds, max_retries, http_get)
    elif package_id == "HIST-OECD-CLI-MACRO-CYCLE-V1":
        result = _optional_failed(package_id, "OECD public endpoint not configured", paths, start_date, end_date)
    else:
        result = _optional_failed(package_id, "package downloader not configured", paths, start_date, end_date)
    result["resolution"] = {key: resolution.get(key) for key in ["selected_source", "source_type", "status", "reason"]}
    result["warnings"].extend(warnings)
    _write_package_artifacts(result, paths)
    return result


def _load_local_package(package_id: str, local_file: Path, paths: ProjectPaths, start_date: str, end_date: str) -> dict[str, Any]:
    output = project_path(paths, PACKAGE_SPECS[package_id].output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(local_file.read_bytes())
    return _package_result(package_id, "loaded_from_local", "local_authorized_export", output, start_date, end_date, warnings=[])


def _load_fixture_package(package_id: str, paths: ProjectPaths, start_date: str, end_date: str) -> dict[str, Any]:
    fixture_map = {
        "HIST-ETF-OHLCV-CN-HK-V1": "etf_ohlcv_sample.csv",
        "HIST-BENCHMARK-INDEX-CN-HK-V1": "benchmark_index_sample.csv",
        "HIST-FX-USDCNY-V1": "fred_usdcny_sample.csv",
        "HIST-GLOBAL-RISK-VIX-V1": "fred_vix_sample.csv",
        "HIST-RATES-LIQUIDITY-V1": "fred_rates_sample.csv",
        "HIST-COMMODITY-INFLATION-RISK-V1": "commodity_sample.csv",
        "HIST-POLICY-UNCERTAINTY-EPU-V1": "epu_sample.csv",
        "HIST-OECD-CLI-MACRO-CYCLE-V1": "oecd_cli_sample.csv",
        AUTHORIZED_GB_PACKAGE_ID: "auth_global_briefing_sample.jsonl",
    }
    source = fixture_path(paths, fixture_map[package_id])
    if not source.exists():
        return _optional_failed(package_id, f"fixture missing: {source.name}", paths, start_date, end_date)
    output = project_path(paths, PACKAGE_SPECS[package_id].output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(source.read_bytes())
    status = "loaded_from_local" if package_id != AUTHORIZED_GB_PACKAGE_ID else "downloaded"
    return _package_result(package_id, status, "fixture", output, start_date, end_date, warnings=["fixture source used for tests"])


def _download_etf_package(paths: ProjectPaths, start_date: str, end_date: str, timeout: int, retries: int, http_get: HttpGet) -> dict[str, Any]:
    rows = []
    warnings = []
    for symbol, meta in ETF_UNIVERSE.items():
        try:
            rows.extend(_yahoo_rows(str(meta["yahoo"]), start_date, end_date, timeout, retries, http_get, symbol=symbol, benchmark_id=None, currency=str(meta["currency"]), exchange=str(meta["exchange"])))
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"{symbol}: {exc}")
    if not rows:
        return _failed_package("HIST-ETF-OHLCV-CN-HK-V1", "no ETF rows downloaded", paths, start_date, end_date, warnings)
    output = project_path(paths, PACKAGE_SPECS["HIST-ETF-OHLCV-CN-HK-V1"].output_path)
    write_csv_rows(output, rows, ["date", "symbol", "open", "high", "low", "close", "adjusted_close", "volume", "amount", "currency", "exchange", "source", "downloaded_at"])
    sidecar = output.with_suffix(".json")
    sidecar.write_text(json.dumps({"package_id": "HIST-ETF-OHLCV-CN-HK-V1", "symbols": list(ETF_UNIVERSE), "row_count": len(rows)}, indent=2), encoding="utf-8")
    return _package_result("HIST-ETF-OHLCV-CN-HK-V1", "downloaded", "yahoo_query_or_equivalent_authorized_market_data_source", output, start_date, end_date, warnings=warnings)


def _download_benchmark_package(paths: ProjectPaths, start_date: str, end_date: str, timeout: int, retries: int, http_get: HttpGet) -> dict[str, Any]:
    rows = []
    warnings = []
    for benchmark_id, meta in BENCHMARK_UNIVERSE.items():
        try:
            rows.extend(_yahoo_rows(str(meta["yahoo"]), start_date, end_date, timeout, retries, http_get, symbol=None, benchmark_id=benchmark_id, currency="", exchange=""))
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"{benchmark_id}: {exc}")
    cash_rows = _cash_rows(start_date, end_date)
    rows.extend(cash_rows)
    output = project_path(paths, PACKAGE_SPECS["HIST-BENCHMARK-INDEX-CN-HK-V1"].output_path)
    write_csv_rows(output, rows, ["date", "benchmark_id", "open", "high", "low", "close", "adjusted_close", "volume", "source", "downloaded_at"])
    return _package_result("HIST-BENCHMARK-INDEX-CN-HK-V1", "downloaded", "yahoo_query_or_equivalent_authorized_market_data_source", output, start_date, end_date, warnings=warnings)


def _download_fred_package(package_id: str, paths: ProjectPaths, start_date: str, end_date: str, timeout: int, retries: int, http_get: HttpGet) -> dict[str, Any]:
    series = FRED_SERIES[package_id]
    rows = []
    warnings = []
    source = "fred"
    fred_timeout = min(timeout, 5)
    for fred_id, output_id in series.items():
        try:
            rows.extend(_fred_rows(fred_id, output_id, package_id, start_date, end_date, fred_timeout, retries, http_get))
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"{fred_id}: {exc}")
    if not rows:
        fallback_rows, fallback_source, fallback_warnings = _public_fallback_rows(package_id, start_date, end_date, timeout, retries, http_get)
        rows.extend(fallback_rows)
        warnings.extend(fallback_warnings)
        if fallback_rows:
            source = fallback_source
    if not rows:
        return _optional_failed(package_id, "no FRED rows downloaded", paths, start_date, end_date, warnings)
    output = project_path(paths, PACKAGE_SPECS[package_id].output_path)
    if package_id == "HIST-FX-USDCNY-V1":
        write_csv_rows(output, rows, ["date", "usd_cny", "source", "downloaded_at"])
    elif package_id == "HIST-GLOBAL-RISK-VIX-V1":
        write_csv_rows(output, rows, ["date", "vix_close", "source", "downloaded_at"])
    elif package_id == "HIST-POLICY-UNCERTAINTY-EPU-V1":
        write_csv_rows(output, rows, ["date", "series_id", "value", "frequency", "source", "downloaded_at"])
    else:
        write_csv_rows(output, rows, ["date", "series_id", "value", "source", "downloaded_at"])
    return _package_result(package_id, "downloaded", source, output, start_date, end_date, warnings=warnings)


def _authorized_gb_not_configured(paths: ProjectPaths, start_date: str, end_date: str) -> dict[str, Any]:
    output = project_path(paths, PACKAGE_SPECS[AUTHORIZED_GB_PACKAGE_ID].output_path)
    return {
        "package_id": AUTHORIZED_GB_PACKAGE_ID,
        "status": "not_configured",
        "source": "gb_authorized_api",
        "path": str(output),
        "raw_path": None,
        "normalized_candidate_path": None,
        "row_count": 0,
        "date_min": None,
        "date_max": None,
        "coverage_ratio": 0.0,
        "sha256": None,
        "provenance_path": None,
        "source_url_host": None,
        "downloaded_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "warnings": ["authorized global-briefing source not configured"],
        "blocking": False,
        "production_global_briefing_package_validated": False,
    }


def _optional_failed(package_id: str, reason: str, paths: ProjectPaths, start_date: str, end_date: str, warnings: list[str] | None = None) -> dict[str, Any]:
    return _failed_package(package_id, reason, paths, start_date, end_date, warnings, status="failed")


def _failed_package(package_id: str, reason: str, paths: ProjectPaths, start_date: str, end_date: str, warnings: list[str] | None = None, *, status: str = "failed") -> dict[str, Any]:
    output = project_path(paths, PACKAGE_SPECS.get(package_id, PACKAGE_SPECS["HIST-RATES-LIQUIDITY-V1"]).output_path)
    return {
        "package_id": package_id,
        "status": status,
        "source": None,
        "path": str(output),
        "raw_path": None,
        "normalized_candidate_path": None,
        "row_count": 0,
        "date_min": None,
        "date_max": None,
        "coverage_ratio": 0.0,
        "sha256": None,
        "provenance_path": None,
        "source_url_host": None,
        "downloaded_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "warnings": [reason, *(warnings or [])],
    }


def _package_result(package_id: str, status: str, source: str, output: Path, start_date: str, end_date: str, warnings: list[str]) -> dict[str, Any]:
    rows = _read_rows_for_result(output)
    date_key = "as_of_date" if output.suffix in {".jsonl", ".raw"} else "date"
    date_min, date_max = package_dates(rows, key=date_key)
    return {
        "package_id": package_id,
        "status": status,
        "source": source,
        "path": str(output),
        "raw_path": str(output),
        "normalized_candidate_path": None,
        "row_count": len(rows),
        "date_min": date_min,
        "date_max": date_max,
        "coverage_ratio": coverage_ratio(date_min, date_max, start_date, end_date),
        "sha256": sha256_file(output),
        "provenance_path": None,
        "source_url_host": _host_for_source(source),
        "downloaded_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "warnings": warnings,
    }


def _read_rows_for_result(path: Path) -> list[dict[str, Any]]:
    if path.suffix in {".jsonl", ".raw"}:
        rows = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    rows.append({"date": "", "raw": line})
        return rows
    if path.suffix == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return [dict(row) for row in csv.DictReader(handle)]
    return []


def _host_for_source(source: str | None) -> str | None:
    return {
        "cboe_vix": "cdn.cboe.com",
        "fred": "fred.stlouisfed.org",
        "yahoo_query_or_equivalent_authorized_market_data_source": "query1.finance.yahoo.com",
        "fixture": None,
        "local_authorized_export": None,
    }.get(str(source), None)


def _write_package_artifacts(result: dict[str, Any], paths: ProjectPaths) -> None:
    package_id = result["package_id"]
    spec = PACKAGE_SPECS[package_id]
    manifest_path = project_path(paths, spec.manifest_path)
    report_path = project_path(paths, spec.report_path)
    provenance_path = paths.data_dir / "global_briefing" / "authorized" / "provenance" / f"{package_id}.json"
    if result.get("path") and result.get("sha256"):
        provenance = {
            "package_id": package_id,
            "source": result.get("source"),
            "source_url_host": result.get("source_url_host"),
            "sha256": result.get("sha256"),
            "downloaded_at": result.get("downloaded_at"),
            "sanitized_url": result.get("sanitized_url"),
            "historical_data_authorization": True,
            "trading_authorization": False,
        }
        provenance_path.parent.mkdir(parents=True, exist_ok=True)
        provenance_path.write_text(json.dumps(provenance, indent=2), encoding="utf-8")
        result["provenance_path"] = str(provenance_path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(package_report_markdown(spec.package_id.replace("-", " "), result), encoding="utf-8")


def _yahoo_rows(
    yahoo_symbol: str,
    start_date: str,
    end_date: str,
    timeout: int,
    retries: int,
    http_get: HttpGet,
    *,
    symbol: str | None,
    benchmark_id: str | None,
    currency: str,
    exchange: str,
) -> list[dict[str, Any]]:
    period1 = int(datetime.fromisoformat(start_date).replace(tzinfo=UTC).timestamp())
    period2 = int((datetime.fromisoformat(end_date).replace(tzinfo=UTC) + timedelta(days=1)).timestamp())
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_symbol}?" + urlencode({"period1": period1, "period2": period2, "interval": "1d", "events": "history"})
    payload = json.loads(_http_get_retry(url, timeout, retries, http_get).decode("utf-8"))
    result = payload["chart"]["result"][0]
    timestamps = result.get("timestamp") or []
    quote = (result.get("indicators", {}).get("quote") or [{}])[0]
    adj = (result.get("indicators", {}).get("adjclose") or [{}])[0].get("adjclose") or []
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    rows = []
    for index, timestamp in enumerate(timestamps):
        open_value = _num_at(quote.get("open"), index)
        high = _num_at(quote.get("high"), index)
        low = _num_at(quote.get("low"), index)
        close = _num_at(quote.get("close"), index)
        if close is None or open_value is None or high is None or low is None:
            continue
        row = {
            "date": datetime.fromtimestamp(int(timestamp), UTC).date().isoformat(),
            "open": open_value,
            "high": high,
            "low": low,
            "close": close,
            "adjusted_close": _num_at(adj, index) or close,
            "volume": _num_at(quote.get("volume"), index) or 0,
            "source": "yahoo_query_or_equivalent_authorized_market_data_source",
            "downloaded_at": now,
        }
        if symbol:
            row.update({"symbol": symbol, "amount": "", "currency": currency, "exchange": exchange})
        if benchmark_id:
            row.update({"benchmark_id": benchmark_id})
        rows.append(row)
    return rows


def _fred_rows(fred_id: str, output_id: str, package_id: str, start_date: str, end_date: str, timeout: int, retries: int, http_get: HttpGet) -> list[dict[str, Any]]:
    url = "https://fred.stlouisfed.org/graph/fredgraph.csv?" + urlencode({"id": fred_id, "observation_start": start_date, "observation_end": end_date})
    text = _http_get_retry(url, timeout, retries, http_get).decode("utf-8")
    reader = csv.DictReader(text.splitlines())
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    rows = []
    for row in reader:
        day = row.get("observation_date") or row.get("DATE") or row.get("date")
        value = row.get(fred_id) or row.get("VALUE") or row.get("value")
        if not day or value in (None, "", "."):
            continue
        if package_id == "HIST-FX-USDCNY-V1":
            rows.append({"date": day, "usd_cny": value, "source": "fred", "downloaded_at": now})
        elif package_id == "HIST-GLOBAL-RISK-VIX-V1":
            rows.append({"date": day, "vix_close": value, "source": "fred", "downloaded_at": now})
        elif package_id == "HIST-POLICY-UNCERTAINTY-EPU-V1":
            rows.append({"date": day, "series_id": output_id, "value": value, "frequency": "daily", "source": "fred", "downloaded_at": now})
        else:
            rows.append({"date": day, "series_id": output_id, "value": value, "source": "fred", "downloaded_at": now})
    return rows


def _public_fallback_rows(package_id: str, start_date: str, end_date: str, timeout: int, retries: int, http_get: HttpGet) -> tuple[list[dict[str, Any]], str, list[str]]:
    warnings: list[str] = []
    if package_id == "HIST-GLOBAL-RISK-VIX-V1":
        try:
            return _cboe_vix_rows(start_date, end_date, timeout, retries, http_get), "cboe_vix", warnings
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"CBOE_VIX: {exc}")
        try:
            return _yahoo_close_rows("^VIX", "vix_close", package_id, start_date, end_date, timeout, retries, http_get), "yahoo_query_or_equivalent_authorized_market_data_source", warnings
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"^VIX: {exc}")
        return [], "cboe_vix", warnings
    if package_id == "HIST-FX-USDCNY-V1":
        try:
            rows = _yahoo_close_rows("CNY=X", "usd_cny", package_id, start_date, end_date, timeout, retries, http_get)
            warnings.append("FRED DEXCHUS unavailable; used Yahoo CNY=X historical close fallback.")
            return rows, "yahoo_query_or_equivalent_authorized_market_data_source", warnings
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"CNY=X: {exc}")
        return [], "yahoo_query_or_equivalent_authorized_market_data_source", warnings
    if package_id == "HIST-RATES-LIQUIDITY-V1":
        rows = []
        fallback_symbols = {
            "^FVX": "US_5Y_YAHOO_FVX",
            "^TNX": "US_10Y_YAHOO_TNX",
            "^IRX": "US_13W_YAHOO_IRX",
        }
        for yahoo_symbol, output_id in fallback_symbols.items():
            try:
                rows.extend(_yahoo_close_rows(yahoo_symbol, output_id, package_id, start_date, end_date, timeout, retries, http_get))
            except Exception as exc:  # noqa: BLE001
                warnings.append(f"{yahoo_symbol}: {exc}")
        if rows:
            warnings.append("FRED rates series unavailable; used Yahoo market-yield proxies where available.")
        return rows, "yahoo_query_or_equivalent_authorized_market_data_source", warnings
    if package_id == "HIST-COMMODITY-INFLATION-RISK-V1":
        rows = []
        fallback_symbols = {
            "CL=F": "WTI_YAHOO_CL_F",
            "BZ=F": "BRENT_YAHOO_BZ_F",
            "GC=F": "GOLD_YAHOO_GC_F",
            "HG=F": "COPPER_YAHOO_HG_F",
        }
        for yahoo_symbol, output_id in fallback_symbols.items():
            try:
                rows.extend(_yahoo_close_rows(yahoo_symbol, output_id, package_id, start_date, end_date, timeout, retries, http_get))
            except Exception as exc:  # noqa: BLE001
                warnings.append(f"{yahoo_symbol}: {exc}")
        if rows:
            warnings.append("FRED commodity series unavailable; used Yahoo futures proxy fallback where available.")
        return rows, "yahoo_query_or_equivalent_authorized_market_data_source", warnings
    if package_id == "HIST-POLICY-UNCERTAINTY-EPU-V1":
        warnings.append("no public EPU fallback configured after FRED failure")
    return [], "fred", warnings


def _cboe_vix_rows(start_date: str, end_date: str, timeout: int, retries: int, http_get: HttpGet) -> list[dict[str, Any]]:
    url = "https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv"
    text = _http_get_retry(url, timeout, retries, http_get).decode("utf-8")
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    start = datetime.fromisoformat(start_date).date()
    end = datetime.fromisoformat(end_date).date()
    rows = []
    for row in csv.DictReader(text.splitlines()):
        raw_day = row.get("DATE") or row.get("Date") or row.get("date")
        value = row.get("CLOSE") or row.get("Close") or row.get("close")
        if not raw_day or value in (None, "", "."):
            continue
        day = datetime.strptime(raw_day, "%m/%d/%Y").date()
        if day < start or day > end:
            continue
        rows.append({"date": day.isoformat(), "vix_close": value, "source": "cboe_vix", "downloaded_at": now})
    return rows


def _yahoo_close_rows(yahoo_symbol: str, output_id: str, package_id: str, start_date: str, end_date: str, timeout: int, retries: int, http_get: HttpGet) -> list[dict[str, Any]]:
    period1 = int(datetime.fromisoformat(start_date).replace(tzinfo=UTC).timestamp())
    period2 = int((datetime.fromisoformat(end_date).replace(tzinfo=UTC) + timedelta(days=1)).timestamp())
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_symbol}?" + urlencode({"period1": period1, "period2": period2, "interval": "1d", "events": "history"})
    payload = json.loads(_http_get_retry(url, timeout, retries, http_get).decode("utf-8"))
    result = payload["chart"]["result"][0]
    timestamps = result.get("timestamp") or []
    quote = (result.get("indicators", {}).get("quote") or [{}])[0]
    closes = quote.get("close") or []
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    rows = []
    for index, timestamp in enumerate(timestamps):
        value = _num_at(closes, index)
        if value is None:
            continue
        day = datetime.fromtimestamp(int(timestamp), UTC).date().isoformat()
        if package_id == "HIST-FX-USDCNY-V1":
            rows.append({"date": day, "usd_cny": value, "source": "yahoo_query_or_equivalent_authorized_market_data_source", "downloaded_at": now})
        elif package_id == "HIST-GLOBAL-RISK-VIX-V1":
            rows.append({"date": day, "vix_close": value, "source": "yahoo_query_or_equivalent_authorized_market_data_source", "downloaded_at": now})
        else:
            rows.append({"date": day, "series_id": output_id, "value": value, "source": "yahoo_query_or_equivalent_authorized_market_data_source", "downloaded_at": now})
    return rows


def _cash_rows(start_date: str, end_date: str) -> list[dict[str, Any]]:
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    start = datetime.fromisoformat(start_date).date()
    end = datetime.fromisoformat(end_date).date()
    rows = []
    current = start
    while current <= end:
        rows.append({"date": current.isoformat(), "benchmark_id": "CASH", "open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0, "adjusted_close": 1.0, "volume": 0, "source": "synthetic_cash_benchmark", "downloaded_at": now})
        current += timedelta(days=1)
    return rows


def _num_at(values: Any, index: int) -> float | None:
    if not isinstance(values, list) or index >= len(values) or values[index] is None:
        return None
    try:
        return float(values[index])
    except (TypeError, ValueError):
        return None


def _http_get_retry(url: str, timeout: int, retries: int, http_get: HttpGet) -> bytes:
    last_error: Exception | None = None
    for attempt in range(1, max(1, retries) + 1):
        try:
            return http_get(url, timeout)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt < retries:
                time.sleep(min(1.0, 0.2 * attempt))
    raise RuntimeError(f"download failed from {source_host(url)}: {last_error}") from last_error


def _default_http_get(url: str, timeout: int) -> bytes:
    request = Request(sanitize_url(url), headers={"User-Agent": "trading-core-research/0.5.7"})
    # Use original URL with sanitized secret-free query. v0.5.7 public endpoints do not require secrets.
    with urlopen(request, timeout=timeout) as response:  # noqa: S310 - approved public historical data endpoints only.
        return response.read()


def build_download_manifest_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Historical Data Download Manifest",
            "",
            "## Scope",
            TRADING_AUTHORIZATION_NOTICE,
            "This workflow downloads or loads historical research packages only.",
            "",
            "## Summary",
            *[f"- {key}: {value}" for key, value in payload["summary"].items()],
            "",
            "## Packages",
            *[f"- {item['package_id']}: status={item['status']} source={item.get('source')} rows={item.get('row_count')} path={item.get('path')}" for item in payload["packages"]],
            "",
            "## Boundary",
            "- historical data download only",
            "- no broker/account/order/trade/position/margin data",
            "- no main ledger write",
            "- no run-daily call",
            "- no forward dry-run started",
            "",
        ]
    )
