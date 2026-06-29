from pathlib import Path

from tests.a_share_owner_dashboard_test_utils import make_paths
from trading_core.equity_owner_remediation.remediation_source_trace import build_remediation_source_trace, forbidden_source_path_hits


def test_source_trace_complete_and_blocks_forbidden_paths(tmp_path):
    paths = make_paths(tmp_path)
    source = paths.project_root / "data" / "source.json"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text("{}", encoding="utf-8")
    trace = build_remediation_source_trace(
        paths=paths,
        as_of_date="2026-06-26",
        generated_at="now",
        source_paths=[source],
        output_paths=[],
        issue_catalog={"issues": [{"source_artifact": "source"}]},
    )
    assert trace["source_trace_complete"] is True
    assert forbidden_source_path_hits([{"path": Path("data/orders/x.json").as_posix()}])
