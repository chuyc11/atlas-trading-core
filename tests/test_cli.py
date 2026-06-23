from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from trading_core import cli
from trading_core.storage.file_paths import project_paths


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_cli_help_runs_as_module() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "trading_core.cli", "--help"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "trading-core" in result.stdout
    assert "Planned commands" in result.stdout


def test_issue_1_skeleton_exists() -> None:
    expected_paths = [
        "pyproject.toml",
        "README.md",
        "src/trading_core/__init__.py",
        "src/trading_core/cli.py",
        "config",
        "data/signals",
        "data/orders",
        "data/trades",
        "data/portfolios",
        "data/valuations",
        "outputs/daily",
        "tests",
    ]

    for relative_path in expected_paths:
        assert (PROJECT_ROOT / relative_path).exists(), relative_path


def test_cli_resolves_workspace_style_paths(tmp_path: Path) -> None:
    paths = project_paths(tmp_path)

    resolved = cli._resolve_cli_path(r"work\trading-core\data\raw\prices\etf_daily", paths)

    assert resolved == tmp_path / "work" / "trading-core" / "data" / "raw" / "prices" / "etf_daily"
