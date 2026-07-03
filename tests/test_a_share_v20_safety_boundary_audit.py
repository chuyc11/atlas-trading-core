from __future__ import annotations

from pathlib import Path

from a_share_v20_test_utils import make_v20_paths
from trading_core.equity_v20_platform_closeout.audit import audit_a_share_v20_platform_closeout
from trading_core.equity_v20_platform_closeout.builder import run_a_share_v20_platform_closeout


def test_v20_audit_passes_and_blocks_mutated_forbidden_field(tmp_path: Path) -> None:
    paths = make_v20_paths(tmp_path)
    run_a_share_v20_platform_closeout(paths=paths, simulation_only=True)
    audit = audit_a_share_v20_platform_closeout(paths=paths)
    assert audit["overall_passed"] is True

    result_path = paths.data_dir / "equity_v20_platform_closeout" / "daily" / "2026-07-01" / "v20_platform_closeout_result.json"
    text = result_path.read_text(encoding="utf-8").replace('"real_orders_placed": false', '"real_orders_placed": true', 1)
    result_path.write_text(text, encoding="utf-8")

    blocked = audit_a_share_v20_platform_closeout(paths=paths)
    assert blocked["overall_passed"] is False
    assert "required_false_not_false:real_orders_placed" in blocked["blocking_reasons"]
