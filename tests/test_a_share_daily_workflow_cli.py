from __future__ import annotations

from pathlib import Path

import pytest

from a_share_daily_workflow_test_utils import make_workflow_paths
from a_share_feature_test_utils import AS_OF_DATE


def test_daily_workflow_cli_smoke_no_run_daily(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_workflow_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    assert cli.main(["preflight-a-share-daily-workflow", "--as-of-date", AS_OF_DATE]) == 0
    assert cli.main(["run-a-share-daily-research-workflow", "--as-of-date", AS_OF_DATE, "--mode", "validate_existing_artifacts"]) == 0
    assert cli.main(["audit-a-share-daily-research-workflow", "--as-of-date", AS_OF_DATE]) == 0
    assert cli.main(["run-and-audit-a-share-daily-research-workflow", "--as-of-date", AS_OF_DATE, "--mode", "validate_existing_artifacts"]) == 0
