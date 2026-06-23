from __future__ import annotations

import subprocess
import sys
from pathlib import Path


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
