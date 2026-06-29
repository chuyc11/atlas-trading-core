from trading_core.cli import build_parser


def test_current_day_cli_commands_parse():
    parser = build_parser()
    args = parser.parse_args(
        [
            "run-a-share-current-day-research",
            "--as-of-date",
            "2026-06-26",
            "--mode",
            "run_research_from_existing_refresh",
            "--workflow-mode",
            "validate_existing_artifacts",
        ]
    )
    assert args.command == "run-a-share-current-day-research"
    assert args.workflow_mode == "validate_existing_artifacts"

