from __future__ import annotations

from pathlib import Path

from a_share_daily_workflow_test_utils import make_workflow_paths
from a_share_feature_test_utils import AS_OF_DATE
from trading_core.equity_workflows.workflow_runner import run_a_share_daily_research_workflow


def test_build_from_existing_data_calls_only_allowed_a_share_research_commands(tmp_path: Path) -> None:
    paths = make_workflow_paths(tmp_path)
    commands: list[str] = []

    def executor(definition, config, project_paths):
        commands.append(definition["build_command"])
        return {"overall_passed": True, "blocking_reasons": [], "warnings": []}

    result = run_a_share_daily_research_workflow(
        paths=paths,
        as_of_date=AS_OF_DATE,
        mode="build_from_existing_data",
        stage_executor=executor,
    )

    assert result["workflow_run_manifest"]["overall_passed"] is True
    assert len(commands) == 7
    assert all("python -m trading_core.cli" in command for command in commands)
    assert not any("run-daily" in command or "run_daily" in command for command in commands)
    assert not any("broker" in command for command in commands)
