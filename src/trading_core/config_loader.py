"""Configuration loading for JSON-compatible YAML files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_CONFIG_DIR = PROJECT_ROOT / "config"
PACKAGE_CONFIG_DIR = Path(__file__).resolve().with_name("config_defaults")
CONFIG_DIR = SOURCE_CONFIG_DIR if SOURCE_CONFIG_DIR.is_dir() else PACKAGE_CONFIG_DIR


def load_config(name: str, config_dir: Path | None = None) -> dict[str, Any]:
    """Load a config file from the local config directory.

    The project keeps simple JSON-compatible YAML documents so the first-stage
    runtime stays dependency-free.
    """

    base = config_dir or CONFIG_DIR
    path = base / name
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def load_all_configs(config_dir: Path | None = None) -> dict[str, dict[str, Any]]:
    names = [
        "settings.yaml",
        "universe_china_etf.yaml",
        "broker_rules.yaml",
        "risk_rules.yaml",
        "benchmarks.yaml",
        "evolution.yaml",
        "report.yaml",
        "admission_rules.yaml",
    ]
    return {name: load_config(name, config_dir) for name in names}
