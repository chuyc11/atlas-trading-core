from tests.a_share_build_output_dashboard_test_utils import AS_OF_DATE, make_paths, write_text
from trading_core.equity_build_output_dashboard.build_output_source_trace import build_source_trace


def test_build_output_source_trace_complete(tmp_path):
    paths = make_paths(tmp_path)
    source = paths.data_dir / "source.json"
    write_text(source, "{}")
    result = build_source_trace(paths=paths, as_of_date=AS_OF_DATE, source_artifacts={"source": source}, output_artifacts={}, source_resolution={})
    assert result["source_trace_complete"] is True
    assert result["entries"][0]["sha256"]

