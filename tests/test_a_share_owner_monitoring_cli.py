from trading_core.cli import build_parser


def test_owner_monitoring_cli_commands_parse():
    parser = build_parser()
    args = parser.parse_args(["build-a-share-owner-monitoring", "--as-of-date", "2026-06-26", "--mode", "build_monitoring_dashboard", "--history-window-days", "30"])
    assert args.command == "build-a-share-owner-monitoring"
    assert args.history_window_days == 30
