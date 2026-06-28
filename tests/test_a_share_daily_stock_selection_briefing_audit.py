from __future__ import annotations

from pathlib import Path

from a_share_daily_stock_selection_briefing_test_utils import briefing_output_dir, build_briefing_package, make_briefing_paths
from a_share_feature_test_utils import AS_OF_DATE
from trading_core.equity_briefings.briefing_audit import audit_a_share_daily_stock_selection_briefing


def test_briefing_audit_passes_and_fails_for_forbidden_positive_wording(tmp_path: Path) -> None:
    paths = make_briefing_paths(tmp_path)
    build_briefing_package(paths)

    audit = audit_a_share_daily_stock_selection_briefing(paths=paths, as_of_date=AS_OF_DATE)
    assert audit["overall_passed"] is True
    assert audit["blocking_reasons"] == []
    assert all(audit["required_sections"].values())

    report_path = briefing_output_dir(paths) / "DAILY_STOCK_SELECTION_BRIEFING.md"
    report_path.write_text(report_path.read_text(encoding="utf-8") + "\n这是买入建议。\n", encoding="utf-8")
    failed = audit_a_share_daily_stock_selection_briefing(paths=paths, as_of_date=AS_OF_DATE)

    assert failed["overall_passed"] is False
    assert "no_forbidden_wording=false" in failed["blocking_reasons"]


def test_briefing_audit_allows_required_negative_disclaimers(tmp_path: Path) -> None:
    paths = make_briefing_paths(tmp_path)
    build_briefing_package(paths)

    audit = audit_a_share_daily_stock_selection_briefing(paths=paths, as_of_date=AS_OF_DATE)

    assert audit["checks"]["no_forbidden_wording"] is True
    assert audit["recommended_next_version"] == "v0.7.8-a-share-virtual-portfolio-tracking-and-paper-ledger"
