from trading_core.cli import build_parser


def test_gated_build_cli_commands_parse():
    parser = build_parser()
    args = parser.parse_args(["build-a-share-gated-build-from-existing-data", "--as-of-date", "2026-06-26", "--mode", "run_gated_build_from_existing_data"])
    assert args.command == "build-a-share-gated-build-from-existing-data"
    args = parser.parse_args(["audit-a-share-gated-build-from-existing-data", "--as-of-date", "2026-06-26"])
    assert args.command == "audit-a-share-gated-build-from-existing-data"

