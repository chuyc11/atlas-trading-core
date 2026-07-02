from __future__ import annotations

from pathlib import Path

from a_share_v11_test_utils import make_v11_paths, v11_json
from trading_core.equity_v11_owner_ops_platform.builder import run_a_share_v11_owner_ops_platform


def test_v11_owner_command_center_generation_includes_claim_guard_state(tmp_path: Path) -> None:
    paths = make_v11_paths(tmp_path)
    result = run_a_share_v11_owner_ops_platform(paths=paths, simulation_only=True)
    command = v11_json(paths, "v11_owner_command_center_result")

    assert result["owner_command_center_generated"] is True
    assert command["dashboard_summary_json_generated"] is True
    assert command["dashboard_markdown_generated"] is True
    assert command["performance_claim_guard_status"]["benchmark_relative_claim_allowed"] is False
    assert command["performance_claim_guard_status"]["real_performance_claim_allowed"] is False
    assert command["recommended_next_operator_action"]


def test_v11_owner_command_center_blocks_unsupported_performance_claims(tmp_path: Path) -> None:
    paths = make_v11_paths(tmp_path)
    run_a_share_v11_owner_ops_platform(paths=paths, simulation_only=True)
    benchmark = v11_json(paths, "v11_benchmark_claim_guard_integration_result")

    assert benchmark["unsupported_excess_return_blocked"] is True
    assert benchmark["unsupported_tracking_error_blocked"] is True
    assert benchmark["unsupported_relative_drawdown_blocked"] is True
    assert benchmark["simulation_only_performance_statement_allowed_with_disclaimer"] is True
