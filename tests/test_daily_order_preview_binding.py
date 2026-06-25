from pathlib import Path

import pytest

from daily_workflow_test_utils import AS_OF, make_daily_workflow_paths
from global_briefing_test_utils import assert_no_protected_paths
from trading_core.daily_workflow.daily_order_preview_binding import build_daily_order_preview


def test_daily_order_preview(tmp_path: Path) -> None:
    paths = make_daily_workflow_paths(tmp_path)
    result = build_daily_order_preview(as_of_date=AS_OF, strategy="all", execution_mode="isolated", paths=paths)
    assert result["proposal_count"] > 0
    assert result["preview_only"] is True
    assert result["executed"] is False
    for proposal in result["proposals"]:
        assert proposal["execution_earliest_date"] > AS_OF
        assert proposal["quantity"] % 100 == 0
        assert proposal["cash_buffer_applied"] is True
        assert "reject_reason" in proposal
    assert not (paths.data_dir / "strategies" / "order_previews" / f"daily_order_preview-{AS_OF}.json").exists()
    assert_no_protected_paths(paths)


def test_daily_order_preview_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_daily_workflow_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["daily-order-preview", "--as-of-date", AS_OF, "--strategy", "all", "--execution-mode", "isolated"]) == 0

