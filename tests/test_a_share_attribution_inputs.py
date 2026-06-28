from __future__ import annotations

from pathlib import Path

from a_share_attribution_test_utils import make_attribution_paths
from trading_core.equity_attribution.attribution_inputs import load_attribution_inputs


def test_attribution_inputs_load_required_baseline(tmp_path: Path) -> None:
    paths = make_attribution_paths(tmp_path)
    inputs = load_attribution_inputs(paths=paths)
    assert inputs.audits["performance_audit"]["overall_passed"] is True
    assert inputs.performance["performance_summary"]["recommended_next_version"].startswith("v0.7.12")
    assert set(inputs.holdings_by_key) == {"long", "mid", "short"}
