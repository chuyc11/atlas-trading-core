from __future__ import annotations

from pathlib import Path

from a_share_candidate_test_utils import build_candidate_package, make_candidate_paths, relaxed_candidate_config
from a_share_feature_test_utils import AS_OF_DATE
from trading_core.equity_selection.candidate_generation_audit import audit_a_share_candidates


def test_candidate_generation_boundaries_block_portfolios_buy_sell_and_order_preview(tmp_path: Path) -> None:
    paths = make_candidate_paths(tmp_path)
    build_candidate_package(paths, relaxed_candidate_config())
    output_dir = paths.outputs_dir / "equity_selection" / "daily" / AS_OF_DATE
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "BUY_LIST.md").write_text("forbidden", encoding="utf-8")
    (output_dir / "ORDER_PREVIEW.md").write_text("forbidden", encoding="utf-8")
    (paths.data_dir / "equity_portfolios").mkdir(parents=True, exist_ok=True)

    audit = audit_a_share_candidates(paths=paths, as_of_date=AS_OF_DATE, minimum_strict_count=1)
    assert audit["overall_passed"] is False
    assert audit["forbidden_artifacts"]["buy_sell_signal_artifacts_present"]
    assert audit["forbidden_artifacts"]["order_preview_artifacts_present"]
    assert audit["forbidden_artifacts"]["virtual_portfolio_artifacts_present"]
    assert "no_buy_sell_signal_artifacts_generated=false" in audit["blocking_reasons"]
