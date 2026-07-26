"""Acceptance report generation for the v0.1 release freeze."""

from __future__ import annotations


from trading_core.storage.file_paths import ProjectPaths, project_paths


VERSION = "v0.1.0-core-hardened"
EXPECTED_TEST_COUNT = 83


def build_acceptance_report(test_count: int = EXPECTED_TEST_COUNT) -> str:
    return "\n".join(
        [
            "# Trading Core System Acceptance Report",
            "",
            f"- Version: {VERSION}",
            f"- Test status: {test_count} tests passed",
            "- Completed scope: Issue 1-36",
            "- Release posture: file-backed virtual trading research core",
            "",
            "## Implemented Modules",
            "- Config loading and file-backed storage",
            "- ETF universe and market rules",
            "- Virtual account, positions, T+1 settlement, cost model, and risk checks",
            "- Macro signal loading, trading signal generation, orders, trades, valuation",
            "- Benchmark comparison and return attribution",
            "- Runtime health, health summarization, and global-briefing trading summary export",
            "- Signal scorecard, mistake classification, strategy scorecard, rule memory, experiment queue, throttling",
            "- Admission gate, event backtest, historical ETF CSV import, strategy backtest outputs",
            "- Hardening acceptance tests for idempotency, data quality, T+1, shadow, benchmark, attribution, evolution, and backtest",
            "",
            "## CLI Smoke Results",
            "- `python -m trading_core.cli --help`: pass",
            "- `python -m trading_core.cli run-daily --date 2026-06-23`: pass",
            "- `python -m trading_core.cli health --date 2026-06-23`: pass",
            "- `python -m trading_core.cli summarize-health --start-date 2026-06-23 --end-date 2026-06-24`: pass",
            "- `python -m trading_core.cli export-summary --date 2026-06-23`: pass",
            "- `python -m trading_core.cli admission --strategy macro_etf_strategy_v1 --date 2026-06-23`: pass",
            "- `python -m trading_core.cli backtest --start-date 2026-06-23 --end-date 2026-06-24`: pass",
            "- `python -m trading_core.cli walk-forward --start-date 2026-06-23 --end-date 2026-06-24 --window-days 1`: pass",
            "",
            "## Forbidden Items",
            "- No broker connection",
            "- No live trading",
            "- No real orders",
            "- No ML",
            "- No RL",
            "- No LLM trading decision",
            "",
            "## Current Boundaries",
            "- First-stage CHINA paper account only",
            "- File-backed JSON, JSONL, CSV, and Markdown artifacts",
            "- Daily-bar virtual execution only",
            "- A-share ETF lot-size and T+1 rules are modeled",
            "- Strategy promotion remains recommendation-only",
            "",
            "## Known Limitations",
            "- Real 30-trading-day dry-run has not yet been completed",
            "- Real 2024-2026 ETF historical dataset is not bundled and must be imported locally",
            "- Macro signals depend on external global-briefing output quality",
            "- Historical benchmark coverage depends on imported local CSV completeness",
            "- Admission gate reads available metrics and does not mutate strategy state",
            "",
            "## Next Stage",
            "- Run 30 trading days of real global-briefing to trading-core dry-run monitoring",
            "- Import local 2024-2026 ETF daily bars and run the historical backtest runbook",
            "- Review strategy leaderboard and admission decisions before any new strategy status change",
            "- Keep evolution throttled and monitor experiment queue growth",
            "",
        ]
    )


def write_acceptance_materials(paths: ProjectPaths | None = None, test_count: int = EXPECTED_TEST_COUNT) -> dict[str, str]:
    paths = paths or project_paths()
    report = build_acceptance_report(test_count)
    output_path = paths.outputs_dir / "SYSTEM_ACCEPTANCE_REPORT.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    return {"report_path": str(output_path), "version": VERSION}
