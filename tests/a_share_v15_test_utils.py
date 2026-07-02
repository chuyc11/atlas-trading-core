from __future__ import annotations

import json
from pathlib import Path

from a_share_v14_test_utils import make_v14_paths
from trading_core.equity_v14_portfolio_risk_lab.audit import audit_a_share_v14_portfolio_risk_lab
from trading_core.equity_v14_portfolio_risk_lab.builder import run_a_share_v14_portfolio_risk_lab
from trading_core.equity_v15_market_regime_lab.builder import DEFAULT_AS_OF_DATE, SOURCE_VERSION
from trading_core.storage.file_paths import ProjectPaths


def make_v15_paths(tmp_path: Path) -> ProjectPaths:
    paths = make_v14_paths(tmp_path)
    run_a_share_v14_portfolio_risk_lab(paths=paths, simulation_only=True)
    audit_a_share_v14_portfolio_risk_lab(paths=paths)
    (paths.project_root / "VERSION").write_text(SOURCE_VERSION, encoding="utf-8")
    return paths


def v15_json(paths: ProjectPaths, name: str, *, as_of_date: str = DEFAULT_AS_OF_DATE):
    path = paths.data_dir / "equity_v15_market_regime_lab" / "daily" / as_of_date / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))
