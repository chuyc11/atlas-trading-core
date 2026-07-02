from __future__ import annotations

import json
from pathlib import Path

from a_share_v16_test_utils import make_v16_paths
from trading_core.equity_v16_pit_backtest_market_rules.audit import audit_a_share_v16_pit_backtest_market_rules
from trading_core.equity_v16_pit_backtest_market_rules.builder import run_a_share_v16_pit_backtest_market_rules
from trading_core.equity_v17_strategy_validation_lab.builder import DEFAULT_AS_OF_DATE, SOURCE_VERSION
from trading_core.storage.file_paths import ProjectPaths


def make_v17_paths(tmp_path: Path) -> ProjectPaths:
    paths = make_v16_paths(tmp_path)
    run_a_share_v16_pit_backtest_market_rules(paths=paths, simulation_only=True)
    audit_a_share_v16_pit_backtest_market_rules(paths=paths)
    (paths.project_root / "VERSION").write_text(SOURCE_VERSION, encoding="utf-8")
    return paths


def v17_json(paths: ProjectPaths, name: str, *, as_of_date: str = DEFAULT_AS_OF_DATE):
    path = paths.data_dir / "equity_v17_strategy_validation_lab" / "daily" / as_of_date / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))
