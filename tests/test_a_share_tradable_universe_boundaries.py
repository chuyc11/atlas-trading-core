from __future__ import annotations

import json
from pathlib import Path

from a_share_selection_test_utils import AS_OF_DATE, make_tradable_universe_paths
from trading_core.equity_selection.filter_config import TRADABLE_UNIVERSE_BOUNDARY
from trading_core.equity_selection.tradable_universe_audit import FORBIDDEN_POSITIVE_WORDING, audit_a_share_tradable_universe
from trading_core.equity_selection.tradable_universe_filter import build_a_share_tradable_universe


def test_tradable_universe_boundaries_block_scores_candidates_portfolios_and_live_claims(tmp_path: Path) -> None:
    paths = make_tradable_universe_paths(tmp_path)
    result = build_a_share_tradable_universe(paths=paths)

    assert result["boundary"]["scores_generated"] is False
    assert result["boundary"]["candidates_generated"] is False
    assert result["boundary"]["virtual_portfolio_generated"] is False
    assert result["boundary"]["day2_executed"] is False
    assert result["boundary"]["run_daily_called"] is False
    assert result["boundary"]["broker_connected"] is False
    assert result["boundary"]["real_orders_placed"] is False
    assert result["boundary"]["model_profit_guaranteed"] is False
    assert result["boundary"]["live_trading_ready"] is False
    assert TRADABLE_UNIVERSE_BOUNDARY["official_forward_dry_run_status_unchanged"] is True
    assert '"live_trading_ready": true' in FORBIDDEN_POSITIVE_WORDING

    config_path = paths.data_dir / "equity_selection" / "daily" / AS_OF_DATE / "filter_config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["boundary"]["live_trading_ready"] = True
    config_path.write_text(json.dumps(config), encoding="utf-8")
    audit = audit_a_share_tradable_universe(paths=paths, as_of_date=AS_OF_DATE, minimum_strict_count=1)
    assert audit["overall_passed"] is False
    assert "live_trading_ready_false=false" in audit["blocking_reasons"]
    assert audit["forbidden_wording_hits"]

