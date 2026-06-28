from __future__ import annotations

from pathlib import Path

from a_share_daily_workflow_test_utils import make_workflow_paths, write_root_version
from a_share_feature_test_utils import AS_OF_DATE
from trading_core.equity_workflows.workflow_preflight import preflight_a_share_daily_workflow


def test_daily_workflow_preflight_checks_required_artifacts_and_versions(tmp_path: Path) -> None:
    paths = make_workflow_paths(tmp_path)

    result = preflight_a_share_daily_workflow(paths=paths, as_of_date=AS_OF_DATE)

    assert result["overall_passed"] is True
    assert result["required_artifacts_present"] is True
    assert result["required_upstream_audits_present"] is True
    assert result["required_cli_commands_present"] is True
    assert result["version_consistent"] is True
    assert result["root_import_version"] == "0.7.8"
    assert result["src_import_version"] == "0.7.8"


def test_daily_workflow_preflight_blocks_root_shim_version_mismatch(tmp_path: Path) -> None:
    paths = make_workflow_paths(tmp_path)
    write_root_version(paths, "0.7.7")

    result = preflight_a_share_daily_workflow(paths=paths, as_of_date=AS_OF_DATE)

    assert result["overall_passed"] is False
    assert "version_consistent=false" in result["blocking_reasons"]
