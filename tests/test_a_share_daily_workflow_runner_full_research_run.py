from __future__ import annotations

from pathlib import Path

from a_share_daily_workflow_test_utils import make_workflow_paths
from a_share_feature_test_utils import AS_OF_DATE
from trading_core.equity_workflows.workflow_runner import run_a_share_daily_research_workflow


def test_full_research_run_records_public_refresh_disabled_by_default(tmp_path: Path) -> None:
    paths = make_workflow_paths(tmp_path)
    commands: list[str] = []

    def executor(definition, config, project_paths):
        commands.append(definition["build_command"])
        return {"overall_passed": True, "blocking_reasons": [], "warnings": []}

    result = run_a_share_daily_research_workflow(
        paths=paths,
        as_of_date=AS_OF_DATE,
        mode="full_research_run",
        stage_executor=executor,
    )

    assert result["workflow_config"]["allow_public_data_refresh"] is False
    assert not any("refresh" in command.lower() for command in commands)
    assert result["workflow_run_manifest"]["run_daily_called"] is False
