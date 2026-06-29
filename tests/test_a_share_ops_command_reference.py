from trading_core.equity_ops_center.command_reference import build_ops_command_reference


def test_ops_command_reference_excludes_forbidden_classes():
    ref = build_ops_command_reference(as_of_date="2026-06-26")
    assert ref["safe_owner_commands"]
    assert "broker commands" in ref["excluded_command_classes"]
    assert "order commands" in ref["excluded_command_classes"]
