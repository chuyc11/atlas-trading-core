"""Local file provider for A-share public data snapshots."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import read_json
from trading_core.storage.file_paths import ProjectPaths


def load_local_snapshot(paths: ProjectPaths) -> dict[str, Any]:
    candidates = [
        paths.data_dir / "equity_data_quality" / "local_a_share_snapshot.json",
        paths.project_root / "tests" / "fixtures" / "a_share_data" / "local_a_share_snapshot.json",
    ]
    for path in candidates:
        payload = read_json(path)
        if payload.get("rows"):
            return {
                "provider": "local_file_provider",
                "succeeded": True,
                "source_path": _rel(path, paths.project_root),
                "rows": payload["rows"],
                "external_api_called": False,
                "real_time_market_data_downloaded": False,
                "reason": "",
            }
    return {
        "provider": "local_file_provider",
        "succeeded": False,
        "source_path": "",
        "rows": [],
        "external_api_called": False,
        "real_time_market_data_downloaded": False,
        "reason": "local_a_share_snapshot.json not found",
    }


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()

