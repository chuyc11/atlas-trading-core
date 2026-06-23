"""Command line entry point for the Trading Core project."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from datetime import date as Date

from trading_core import __version__
from trading_core.backtest.event_backtester import run_event_backtest
from trading_core.backtest.historical_backtester import run_historical_backtest
from trading_core.backtest.walk_forward import run_walk_forward
from trading_core.data.historical_prices import import_prices_csv
from trading_core.daily_run import run_daily
from trading_core.evaluation.strategy_leaderboard import build_strategy_leaderboard
from trading_core.evolution.admission_gate import run_admission
from trading_core.reports.acceptance_report import write_acceptance_materials
from trading_core.reports.trading_summary import export_trading_summary
from trading_core.runtime.health import load_health, summarize_health
from trading_core.signals.macro_signal_loader import load_macro_signals
from trading_core.storage.file_paths import ensure_project_dirs, project_paths


PLANNED_COMMANDS = (
    "init",
    "load-macro",
    "generate-signals",
    "generate-orders",
    "execute",
    "mark",
    "benchmark",
    "attribution",
    "score-signals",
    "classify-mistakes",
    "score-strategies",
    "update-rule-memory",
    "update-experiment-queue",
    "run-evolution",
    "report",
    "run-daily",
    "health",
    "export-summary",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading-core",
        description=(
            "File-backed virtual trading research core. "
            "First-stage virtual trading, reporting, evolution, backtest, and walk-forward commands."
        ),
        epilog="Planned commands: " + ", ".join(PLANNED_COMMANDS) + ".",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    subparsers = parser.add_subparsers(dest="command")
    for command in PLANNED_COMMANDS:
        subparser = subparsers.add_parser(command)
        subparser.add_argument("--date", default=Date.today().isoformat())
    backtest = subparsers.add_parser("backtest")
    backtest.add_argument("--start-date", required=True)
    backtest.add_argument("--end-date", required=True)
    backtest.add_argument("--strategy", dest="strategy_id")
    walk = subparsers.add_parser("walk-forward")
    walk.add_argument("--start-date", required=True)
    walk.add_argument("--end-date", required=True)
    walk.add_argument("--window-days", type=int, default=5)
    summarize = subparsers.add_parser("summarize-health")
    summarize.add_argument("--start-date", required=True)
    summarize.add_argument("--end-date", required=True)
    importer = subparsers.add_parser("import-prices")
    importer.add_argument("--input", required=True)
    importer.add_argument("--market", required=True)
    admission = subparsers.add_parser("admission")
    admission.add_argument("--strategy", required=True, dest="strategy_id")
    admission.add_argument("--date", required=True)
    subparsers.add_parser("acceptance-report")
    leaderboard = subparsers.add_parser("leaderboard")
    leaderboard.add_argument("--start-date", required=True)
    leaderboard.add_argument("--end-date", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        return 0
    paths = project_paths()
    if args.command == "init":
        ensure_project_dirs(paths)
        print(f"initialized {paths.project_root}")
        return 0
    if args.command == "load-macro":
        rows, limitations = load_macro_signals(args.date, paths)
        print({"macro_signals": len(rows), "limitations": limitations})
        return 0
    if args.command == "backtest":
        if args.strategy_id:
            result = run_historical_backtest(args.start_date, args.end_date, args.strategy_id)
            print({"days": result["days"], "trades": result["trades_count"], "strategy_id": result["strategy_id"]})
        else:
            result = run_event_backtest(args.start_date, args.end_date)
            print({"days": result["days"], "total_return": result["total_return"]})
        return 0
    if args.command == "walk-forward":
        result = run_walk_forward(args.start_date, args.end_date, args.window_days)
        print({"windows": len(result["windows"])})
        return 0
    if args.command == "summarize-health":
        result = summarize_health(args.start_date, args.end_date)
        print(result)
        return 0
    if args.command == "import-prices":
        from pathlib import Path

        result = import_prices_csv(Path(args.input), args.market)
        print(result)
        return 0
    if args.command == "admission":
        result = run_admission(args.strategy_id, args.date)
        print(result)
        return 0
    if args.command == "acceptance-report":
        result = write_acceptance_materials(paths)
        print(result)
        return 0
    if args.command == "leaderboard":
        result = build_strategy_leaderboard(args.start_date, args.end_date, paths)
        print({"items": len(result["items"]), "report_path": result["report_path"]})
        return 0
    if args.command == "health":
        health = load_health(args.date)
        if health is None:
            health = run_daily(args.date)["health"]
        print(health)
        return 0
    if args.command == "export-summary":
        result = export_trading_summary(args.date)
        print(result)
        return 0
    result = run_daily(args.date)
    print(
        {
            "date": result["date"],
            "signals": len(result["signals"]),
            "orders": len(result["orders"]),
            "trades": len(result["trades"]),
            "limitations": result["limitations"],
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
