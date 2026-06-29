from trading_core.cli import build_parser


def test_owner_remediation_cli_commands_parse():
    parser = build_parser()
    args = parser.parse_args(["build-a-share-owner-remediation", "--as-of-date", "2026-06-26", "--mode", "build_remediation_runbook"])
    assert args.command == "build-a-share-owner-remediation"
    assert args.mode == "build_remediation_runbook"
    args = parser.parse_args(["audit-a-share-owner-remediation", "--as-of-date", "2026-06-26"])
    assert args.command == "audit-a-share-owner-remediation"
