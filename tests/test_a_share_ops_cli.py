from trading_core.cli import build_parser


def test_ops_cli_smoke():
    parser = build_parser()
    args = parser.parse_args(["build-a-share-daily-ops-center", "--as-of-date", "2026-06-26", "--mode", "aggregate_existing_ops_artifacts"])
    assert args.command == "build-a-share-daily-ops-center"
    assert args.mode == "aggregate_existing_ops_artifacts"
    args = parser.parse_args(["audit-a-share-daily-ops-center", "--as-of-date", "2026-06-26"])
    assert args.command == "audit-a-share-daily-ops-center"
