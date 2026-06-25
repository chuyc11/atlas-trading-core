from __future__ import annotations

import json
import shutil
from pathlib import Path

from trading_core.storage.file_paths import ProjectPaths


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = PROJECT_ROOT / "tests" / "fixtures" / "global_briefing"
REAL_FIXTURE_ROOT = PROJECT_ROOT / "tests" / "fixtures" / "global_briefing_real"
HISTORICAL_FIXTURE_ROOT = PROJECT_ROOT / "tests" / "fixtures" / "historical_data"


def make_paths(tmp_path: Path) -> ProjectPaths:
    project = tmp_path / "work" / "trading-core"
    fixture_target = project / "tests" / "fixtures" / "global_briefing"
    fixture_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(FIXTURE_ROOT, fixture_target, dirs_exist_ok=True)
    real_fixture_target = project / "tests" / "fixtures" / "global_briefing_real"
    shutil.copytree(REAL_FIXTURE_ROOT, real_fixture_target, dirs_exist_ok=True)
    historical_fixture_target = project / "tests" / "fixtures" / "historical_data"
    shutil.copytree(HISTORICAL_FIXTURE_ROOT, historical_fixture_target, dirs_exist_ok=True)
    return ProjectPaths(tmp_path)


def write_text(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def write_json(path: Path, payload: dict) -> Path:
    write_text(path, json.dumps(payload, indent=2))
    return path


def fixture_path(paths: ProjectPaths, name: str) -> str:
    return f"tests/fixtures/global_briefing/{name}"


def real_fixture_path(paths: ProjectPaths, name: str) -> str:
    return f"tests/fixtures/global_briefing_real/{name}"


def historical_fixture_path(paths: ProjectPaths, name: str) -> str:
    return f"tests/fixtures/historical_data/{name}"


def protected_paths(paths: ProjectPaths) -> list[Path]:
    return [
        paths.project_root / "data" / "orders",
        paths.project_root / "data" / "trades",
        paths.project_root / "data" / "portfolio",
        paths.project_root / "data" / "accounts",
        paths.project_root / "outputs" / "orders",
        paths.project_root / "outputs" / "trades",
        paths.project_root / "outputs" / "portfolio",
    ]


def assert_no_protected_paths(paths: ProjectPaths) -> None:
    for path in protected_paths(paths):
        assert not path.exists(), path
