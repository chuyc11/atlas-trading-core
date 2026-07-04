from __future__ import annotations

from pathlib import Path

from a_share_v23_test_utils import make_v23_paths, v23_json
from trading_core.equity_v23_operator_ux_journal.builder import REPORT_CATEGORIES, run_a_share_v23_operator_ux_journal


def test_v23_report_artifact_index_has_latest_pointers_and_missing_warning_field(tmp_path: Path) -> None:
    paths = make_v23_paths(tmp_path)
    result = run_a_share_v23_operator_ux_journal(paths=paths, simulation_only=True)
    index = v23_json(paths, "v23_report_artifact_index_result")

    assert result["report_artifact_index_generated"] is True
    assert index["report_category_taxonomy"] == REPORT_CATEGORIES
    assert index["latest_report_pointer"].endswith("A_SHARE_V23_DAILY_RESEARCH_REVIEW.md")
    assert index["latest_result_pointer"].endswith("v23_operator_ux_journal_result.json")
    assert isinstance(index["missing_artifact_warning"], list)
    assert index["files_fabricated"] is False
