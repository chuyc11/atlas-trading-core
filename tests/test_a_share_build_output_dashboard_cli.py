from trading_core.cli import build_parser


def test_build_output_dashboard_cli_parse():
    parser = build_parser()
    args = parser.parse_args(["build-a-share-build-output-owner-dashboard", "--as-of-date", "2026-06-26", "--mode", "build_owner_dashboard_from_build_output"])
    assert args.command == "build-a-share-build-output-owner-dashboard"
    args = parser.parse_args(["audit-a-share-build-output-owner-dashboard", "--as-of-date", "2026-06-26"])
    assert args.command == "audit-a-share-build-output-owner-dashboard"

