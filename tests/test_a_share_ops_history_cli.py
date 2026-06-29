from trading_core.cli import build_parser


def test_ops_history_cli_commands_parse():
    parser = build_parser()
    args = parser.parse_args(["build-a-share-ops-history-baseline", "--as-of-date", "2026-06-26", "--mode", "build_trend_baselines", "--minimum-required-observations", "5"])
    assert args.command == "build-a-share-ops-history-baseline"
    assert args.minimum_required_observations == 5
    args = parser.parse_args(["audit-a-share-ops-history-baseline", "--as-of-date", "2026-06-26"])
    assert args.command == "audit-a-share-ops-history-baseline"

