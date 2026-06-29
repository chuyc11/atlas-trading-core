from tests.a_share_build_repeatability_test_utils import AS_OF_DATE, make_paths, write_text
from trading_core.equity_build_repeatability.repeatability_source_trace import build_repeatability_source_trace


def test_repeatability_source_trace_complete(tmp_path):
    paths = make_paths(tmp_path)
    source = paths.data_dir / "source.json"
    write_text(source, "{}")
    result = build_repeatability_source_trace(paths=paths, as_of_date=AS_OF_DATE, source_artifacts={"source": source}, output_artifacts={})
    assert result["source_trace_complete"] is True
    assert result["entries"][0]["sha256"]

