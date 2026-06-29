from trading_core.cli import build_parser


def test_owner_dashboard_cli_commands_parse():
    parser = build_parser()
    args = parser.parse_args(["build-a-share-owner-dashboard", "--as-of-date", "2026-06-26", "--mode", "build_dashboard_from_existing_run", "--compact-only"])
    assert args.command == "build-a-share-owner-dashboard"
    assert args.compact_only is True
