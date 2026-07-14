import pytest

from trading_core import cli
from trading_core.equity_current_day_builds.execution_plan import build_gated_build_execution_plan


def test_gated_build_execution_plan_uses_build_from_existing_data():
    plan = build_gated_build_execution_plan(as_of_date="2026-06-26", preflight_gate={"overall_passed": True})
    assert "--workflow-mode build_from_existing_data" in plan["workflow_command"]
    assert plan["workflow_argv"][0] == "python"
    assert "run-daily" in plan["commands_forbidden"]


@pytest.mark.parametrize("value", ["2026-02-30", "2026-6-26", "2026-06-26 & whoami", ""])
def test_gated_build_execution_plan_rejects_noncanonical_dates(value):
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        build_gated_build_execution_plan(as_of_date=value, preflight_gate={"overall_passed": True})


def test_gated_build_cli_rejects_noncanonical_date_before_dispatch():
    with pytest.raises(SystemExit) as exc:
        cli.build_parser().parse_args(
            ["build-a-share-gated-build-from-existing-data", "--as-of-date", "2026-06-26;whoami"]
        )
    assert exc.value.code == 2
