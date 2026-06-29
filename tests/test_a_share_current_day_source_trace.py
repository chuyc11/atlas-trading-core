from tests.a_share_current_day_test_utils import AS_OF_DATE, make_paths, seed_data_refresh
from trading_core.equity_current_day.current_day_artifact_index import build_current_day_artifact_index
from trading_core.equity_current_day.current_day_source_trace import build_current_day_source_trace, forbidden_source_path_hits
from trading_core.equity_current_day.data_refresh_link import build_data_refresh_link


def test_current_day_source_trace_complete(tmp_path):
    paths = make_paths(tmp_path)
    seed_data_refresh(paths)
    link = build_data_refresh_link(paths=paths, as_of_date=AS_OF_DATE, resolved_as_of_date=AS_OF_DATE)
    index = build_current_day_artifact_index(paths=paths, as_of_date=AS_OF_DATE, resolved_as_of_date=AS_OF_DATE)
    trace = build_current_day_source_trace(
        paths=paths,
        as_of_date=AS_OF_DATE,
        resolved_as_of_date=AS_OF_DATE,
        generated_at="2026-06-28T00:00:00Z",
        workflow_command="python -m trading_core.cli run-and-audit-a-share-daily-research-workflow",
        data_refresh_link=link,
        artifact_index=index,
        warnings=[],
    )
    assert trace["source_trace_complete"] is True
    assert trace["forbidden_path_hits"] == []


def test_current_day_source_trace_blocks_forbidden_paths():
    assert forbidden_source_path_hits([{"path": "data/orders/orders-2026-06-26.jsonl"}])

