from __future__ import annotations

from pathlib import Path

from a_share_v24_test_utils import build_v24, make_v24_paths, v24_json


def test_v24_cli_hygiene_registers_required_commands_without_forbidden_additions(tmp_path: Path) -> None:
    paths = make_v24_paths(tmp_path)
    build_v24(paths)
    hygiene = v24_json(paths, "v24_cli_hygiene_result")
    result = v24_json(paths, "v24_maintenance_quality_result")

    assert hygiene["cli_hygiene_result_generated"] is True
    assert hygiene["missing_v24_commands"] == []
    assert hygiene["cli_broker_command_added"] is False
    assert hygiene["cli_live_trading_command_added"] is False
    assert hygiene["cli_order_command_added"] is False
    assert hygiene["cli_owner_gate_command_added"] is False
    assert hygiene["old_run_daily_present"] is False
    assert result["old_run_daily_present"] is False
