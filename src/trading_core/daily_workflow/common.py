"""Shared helpers for v0.6.1 daily workflow binding."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from trading_core.execution.common import read_dict, read_rows, rel, standard_boundary
from trading_core.execution.trading_calendar_contract import default_calendar
from trading_core.storage.file_paths import ProjectPaths
from trading_core.storage.jsonl_store import write_json
from trading_core.system.common import default_paths, write_json_markdown
from trading_core.strategies.common import DEFAULT_BENCHMARKS, DEFAULT_UNIVERSE, STRATEGY_IDS


RELEASE_CANDIDATE = "v0.6.1-daily-workflow-binding-audited"
BASELINE_FROM = "v0.6.0-baseline-strategy-pack-audited"
NEXT_VERSION = "v0.6.2-forward-dry-run-start-authorization-pack"
NOTICE = "Daily workflow binding is research-only preview infrastructure and does not start forward dry-run."
DEFAULT_AS_OF_DATE = "2024-12-31"
MARKET_DATA_SOURCE = Path("data/market/historical/authorized/HIST-ETF-OHLCV-CN-HK-V1.csv")
BENCHMARK_DATA_SOURCE = Path("data/market/historical/authorized/HIST-BENCHMARK-INDEX-CN-HK-V1.csv")
RISK_PROXY_SOURCE = Path("data/global_briefing/normalized/GB-AUTHORIZED-FULL-HISTORICAL-PROXY-V1.normalized.jsonl")
PROTECTED_PATHS = [
    "data/orders",
    "data/trades",
    "data/portfolio",
    "data/portfolios",
    "data/accounts",
    "outputs/orders",
    "outputs/trades",
    "outputs/portfolio",
    "outputs/portfolios",
]
WORKFLOW_COMPONENTS = [
    "daily_market_data_snapshot",
    "daily_data_quality_audit",
    "daily_input_freeze_manifest",
    "daily_baseline_signal_binding",
    "daily_order_preview_binding",
    "daily_isolated_execution_preview",
    "daily_report_packet",
    "protected_path_residue_scanner",
    "daily_workflow_audit",
]


def paths_or_default(paths: ProjectPaths | None = None) -> ProjectPaths:
    return default_paths(paths)


def workflow_boundary(scope_key: str) -> dict[str, Any]:
    boundary = standard_boundary(scope_key)
    boundary.update(
        {
            "real_time_market_data_downloaded": False,
            "real_time_download": False,
            "external_api_called": False,
            "external_download_called": False,
            "state_updated": False,
            "manual_confirmation_complete": False,
            "forward_dry_run_start_authorized": False,
            "production_daily_trading_ready": False,
            "ml_trading_approved": False,
            "llm_trading_approved": False,
            "rl_trading_approved": False,
        }
    )
    return boundary


def boundary_markdown(scope: str) -> list[str]:
    return [
        f"- {scope}",
        "- run-daily not called",
        "- forward dry-run not started",
        "- main ledger not written",
        "- no real-time market data download",
        "- ML shadow not used as authorization",
        "- LLM not used for trading decision",
        "- RL not used",
        "- promotion not triggered",
    ]


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_record(paths: ProjectPaths, relative_path: Path) -> dict[str, Any]:
    path = paths.project_root / relative_path
    return {
        "path": relative_path.as_posix(),
        "exists": path.exists(),
        "sha256": sha256_file(path),
    }


def snapshot_path(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "daily_workflow" / "snapshots" / f"daily_market_data_snapshot-{as_of_date}.json"


def snapshot_report_path(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "daily_workflow" / f"DAILY_MARKET_DATA_SNAPSHOT-{as_of_date}.md"


def data_quality_path(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "daily_workflow" / "audits" / f"daily_data_quality_audit-{as_of_date}.json"


def data_quality_report_path(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "audit" / f"DAILY_DATA_QUALITY_AUDIT-{as_of_date}.md"


def freeze_path(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "daily_workflow" / "freeze_manifests" / f"daily_input_freeze_manifest-{as_of_date}.json"


def freeze_report_path(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "daily_workflow" / f"DAILY_INPUT_FREEZE_MANIFEST-{as_of_date}.md"


def daily_signals_path(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "daily_workflow" / "signals" / f"daily_baseline_signals-{as_of_date}.json"


def daily_signals_report_path(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "daily_workflow" / f"DAILY_BASELINE_SIGNALS-{as_of_date}.md"


def daily_order_preview_path(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "daily_workflow" / "order_previews" / f"daily_order_preview-{as_of_date}.json"


def daily_order_preview_report_path(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "daily_workflow" / f"DAILY_ORDER_PREVIEW-{as_of_date}.md"


def execution_preview_path(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "daily_workflow" / "execution_previews" / f"daily_isolated_execution_preview-{as_of_date}.json"


def execution_preview_report_path(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "daily_workflow" / f"DAILY_ISOLATED_EXECUTION_PREVIEW-{as_of_date}.md"


def daily_report_packet_path(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "daily_workflow" / "reports" / f"daily_report_packet-{as_of_date}.json"


def daily_report_packet_markdown_path(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "daily_workflow" / f"DAILY_REPORT_PACKET-{as_of_date}.md"


def read_json_file(path: Path) -> dict[str, Any]:
    return read_dict(path)


def write_artifact(json_path: Path, payload: dict[str, Any], md_path: Path, markdown: str) -> dict[str, Any]:
    write_json_markdown(json_path, payload, md_path, markdown)
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def latest_available_market_date(paths: ProjectPaths) -> str | None:
    source = paths.project_root / MARKET_DATA_SOURCE
    if not source.exists():
        return None
    latest: str | None = None
    with source.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            day = row.get("date")
            symbol = row.get("symbol")
            if symbol in DEFAULT_UNIVERSE and day and (latest is None or day > latest):
                latest = day
    return latest


def market_rows_for_date(paths: ProjectPaths, as_of_date: str) -> dict[str, dict[str, Any]]:
    source = paths.project_root / MARKET_DATA_SOURCE
    rows: dict[str, dict[str, Any]] = {}
    if not source.exists():
        return rows
    with source.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("date") == as_of_date and row.get("symbol") in DEFAULT_UNIVERSE:
                rows[str(row["symbol"])] = row
    return rows


def benchmark_rows_for_date(paths: ProjectPaths, as_of_date: str) -> dict[str, dict[str, Any]]:
    source = paths.project_root / BENCHMARK_DATA_SOURCE
    rows: dict[str, dict[str, Any]] = {}
    if not source.exists():
        return rows
    with source.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            benchmark_id = row.get("benchmark_id")
            if row.get("date") == as_of_date and benchmark_id:
                rows[str(benchmark_id)] = row
    return rows


def risk_proxy_for_date(paths: ProjectPaths, as_of_date: str) -> dict[str, Any] | None:
    source = paths.project_root / RISK_PROXY_SOURCE
    if not source.exists():
        return None
    for row in read_rows(source):
        if row.get("as_of_date") == as_of_date:
            return row
    return None


def price_for_symbol(rows: dict[str, dict[str, Any]], symbol: str) -> float | None:
    row = rows.get(symbol, {})
    raw = row.get("adjusted_close") or row.get("close")
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None
    return value if value > 0 else None


def volume_for_symbol(rows: dict[str, dict[str, Any]], symbol: str) -> float | None:
    row = rows.get(symbol, {})
    try:
        return float(row.get("volume"))
    except (TypeError, ValueError):
        return None


def next_execution_date(as_of_date: str) -> str:
    return default_calendar().next_trading_day(as_of_date, "SSE")


def git_lines(paths: ProjectPaths, args: list[str]) -> list[str]:
    if not (paths.project_root / ".git").exists():
        return []
    result = subprocess.run(["git", *args], cwd=paths.project_root, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line.strip()]


def run_daily_preview(as_of_date: str) -> dict[str, Any]:
    return {
        "command": f"python -m trading_core.cli run-daily --date {as_of_date}",
        "preview_only": True,
        "executed": False,
        "run_daily_called": False,
    }

