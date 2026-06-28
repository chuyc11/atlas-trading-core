from __future__ import annotations

from pathlib import Path

from a_share_daily_stock_selection_briefing_test_utils import briefing_json, build_briefing_package, make_briefing_paths
from trading_core.equity_briefings.briefing_config import SOURCE_TRACE_SECTION_KEYS


def test_briefing_source_trace_covers_every_required_section(tmp_path: Path) -> None:
    paths = make_briefing_paths(tmp_path)
    build_briefing_package(paths)

    trace = briefing_json(paths, "briefing_source_trace")

    assert trace["source_trace_complete"] is True
    assert set(trace["sections"]) == set(SOURCE_TRACE_SECTION_KEYS)
    for record in trace["sections"].values():
        assert record["complete"] is True
        assert record["source_paths"]
        for source in record["source_paths"]:
            assert (paths.project_root / source).exists()
