from trading_core.cli import build_parser


def test_repeatability_cli_commands_parse():
    parser = build_parser()
    args = parser.parse_args(["build-a-share-build-repeatability", "--as-of-date", "2026-06-26", "--mode", "run_repeat_build_from_existing_data"])
    assert args.command == "build-a-share-build-repeatability"
    args = parser.parse_args(["audit-a-share-build-repeatability", "--as-of-date", "2026-06-26"])
    assert args.command == "audit-a-share-build-repeatability"

