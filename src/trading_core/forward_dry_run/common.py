"""Shared helpers for day-0 forward dry-run readiness artifacts."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

from trading_core.global_briefing.historical_data_packages import PROXY_PACKAGE_ID, TRADING_AUTHORIZATION_NOTICE, sha256_file
from trading_core.storage.file_paths import ProjectPaths
from trading_core.storage.jsonl_store import read_json
from trading_core.system.common import default_paths


RELEASE_CANDIDATE = "v0.5.8-day0-operational-readiness-audited"
DAY0_NOTICE = "Day-0 readiness does not start forward dry-run."
PROXY_PACKAGE_FILENAME = f"{PROXY_PACKAGE_ID}.normalized.jsonl"
REQUIRED_FREEZE_PACKAGES = [
    "HIST-ETF-OHLCV-CN-HK-V1",
    "HIST-BENCHMARK-INDEX-CN-HK-V1",
    "HIST-FX-USDCNY-V1",
    "HIST-GLOBAL-RISK-VIX-V1",
    "HIST-RATES-LIQUIDITY-V1",
    "HIST-COMMODITY-INFLATION-RISK-V1",
    "HIST-POLICY-UNCERTAINTY-EPU-V1",
    "HIST-OECD-CLI-MACRO-CYCLE-V1",
]
OPTIONAL_AUTH_GB_PACKAGE = "HIST-AUTH-GLOBAL-BRIEFING-SIGNALS-V1"
AVAILABLE_STATUSES = {"downloaded", "partial_downloaded", "loaded_from_local"}


def paths_or_default(paths: ProjectPaths | None = None) -> ProjectPaths:
    return default_paths(paths)


def resolve_path(raw: str | None, default: Path, paths: ProjectPaths) -> Path:
    if not raw:
        return default
    path = Path(raw)
    return path if path.is_absolute() else paths.project_root / path


def read_dict(path: Path) -> dict[str, Any]:
    payload = read_json(path, default={})
    return payload if isinstance(payload, dict) else {}


def package_by_id(download_manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(item.get("package_id")): item for item in download_manifest.get("packages", []) if isinstance(item, dict)}


def proxy_package_default(paths: ProjectPaths) -> Path:
    return paths.data_dir / "global_briefing" / "normalized" / PROXY_PACKAGE_FILENAME


def rel(path: str | Path | None, paths: ProjectPaths) -> str | None:
    if not path:
        return None
    candidate = Path(path)
    try:
        return candidate.relative_to(paths.project_root).as_posix()
    except ValueError:
        return str(candidate)


def latest_tag(paths: ProjectPaths) -> str | None:
    try:
        result = subprocess.run(["git", "tag", "--points-at", "HEAD"], cwd=paths.project_root, check=False, capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return None
    tags = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return tags[-1] if tags else None


def git_status_clean(paths: ProjectPaths) -> bool | None:
    if not (paths.project_root / ".git").exists():
        return None
    try:
        result = subprocess.run(["git", "status", "--short"], cwd=paths.project_root, check=False, capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() == ""


def has_broker_or_live_config() -> bool:
    prefixes = ("BROKER_", "LIVE_TRADING_", "ALPACA_", "IBKR_")
    return any(key.startswith(prefixes) and value for key, value in os.environ.items())


def standard_boundary(scope_key: str) -> dict[str, Any]:
    return {
        scope_key: True,
        "forward_dry_run_started": False,
        "forward_dry_run_validated": False,
        "run_daily_called": False,
        "main_ledger_written": False,
        "trading_authorization": False,
        "strategy_effectiveness_proven": False,
        "live_trading_ready": False,
        "broker_connected": False,
        "labels_used": False,
        "ml_shadow_used": False,
        "experiments_used": False,
        "promotion_triggered": False,
        "rl_enabled": False,
        "llm_trading_decision": False,
    }


def non_claim_lines() -> list[str]:
    return [
        f"- {DAY0_NOTICE}",
        "- This does not validate forward dry-run.",
        "- This does not prove strategy effectiveness.",
        "- This is not live trading readiness.",
        f"- {TRADING_AUTHORIZATION_NOTICE}",
    ]


def file_record(path: Path, paths: ProjectPaths) -> dict[str, Any]:
    return {
        "path": rel(path, paths),
        "exists": path.exists(),
        "sha256": sha256_file(path),
    }
