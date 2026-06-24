"""Isolated global-briefing historical replay runner."""

from __future__ import annotations

from typing import Any

from trading_core.global_briefing.replay_bundle_builder import _load_price_dates
from trading_core.global_briefing.signal_schema import compact_date, resolve_project_path
from trading_core.reports.research_common import snapshot_protected
from trading_core.storage.file_paths import ProjectPaths
from trading_core.storage.jsonl_store import read_json, write_json, write_jsonl
from trading_core.system.common import default_paths, protected_diff, write_json_markdown


def replay_global_briefing_history(
    bundle_path: str,
    prices_path: str,
    *,
    start_date: str,
    end_date: str,
    initial_cash: float = 1_000_000.0,
    isolated_output_root: str | None = None,
    report_output_root: str | None = None,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    before = snapshot_protected(paths)
    bundle_file = resolve_project_path(bundle_path, paths)
    prices_file = resolve_project_path(prices_path, paths)
    if not bundle_file.exists():
        raise ValueError(f"bundle file missing: {bundle_file}")
    if not prices_file.exists():
        raise ValueError(f"prices file missing: {prices_file}")

    bundle = read_json(bundle_file, default={})
    if not isinstance(bundle, dict) or not isinstance(bundle.get("rows"), list):
        raise ValueError("bundle must be a JSON object with rows")
    price_dates = set(_load_price_dates(prices_path, start_date, end_date, paths))
    selected_rows = [row for row in bundle["rows"] if start_date <= str(row.get("replay_date")) <= end_date]
    replay_id = f"GB-HIST-REPLAY-{compact_date(start_date)}-{compact_date(end_date)}"
    data_root = resolve_project_path(isolated_output_root, paths) if isolated_output_root else paths.data_dir / "replays" / "global_briefing"
    output_root = resolve_project_path(report_output_root, paths) if report_output_root else paths.outputs_dir / "replays" / "global_briefing"

    missing_price_days = [str(row.get("replay_date")) for row in selected_rows if str(row.get("replay_date")) not in price_dates]
    missing_signal_days = [
        str(row.get("replay_date"))
        for row in selected_rows
        if not row.get("selected_signal_generated_at")
    ]
    warnings = ["core execution adapter not isolated; no-trade replay summary generated"]

    isolated_paths = _write_isolated_replay_ledger(
        data_root,
        replay_id,
        selected_rows,
        start_date=start_date,
        end_date=end_date,
        initial_cash=initial_cash,
    )
    protected_changes = protected_diff(paths, before)
    payload: dict[str, Any] = {
        "replay_id": replay_id,
        "start_date": start_date,
        "end_date": end_date,
        "isolated": True,
        "input_bundle": str(bundle_file),
        "input_prices": str(prices_file),
        "warnings": warnings,
        "summary": {
            "replay_days": len(selected_rows),
            "days_processed": len(selected_rows),
            "orders": 0,
            "trades": 0,
            "ending_equity": initial_cash,
            "errors": 0,
        },
        "data_quality": {
            "missing_price_days": missing_price_days,
            "missing_signal_days": missing_signal_days,
        },
        "isolated_output_paths": isolated_paths,
        "protected_path_changes": protected_changes,
        "boundary": {
            "historical_replay_only": True,
            "forward_dry_run": False,
            "live_trading": False,
            "broker_connected": False,
            "main_ledger_written": bool(protected_changes),
            "isolated_replay_ledger_written": True,
            "run_daily_called": False,
            "strategy_state_changed": False,
            "promotion_triggered": False,
            "labels_used": False,
            "ml_shadow_used": False,
            "experiments_used": False,
        },
    }
    json_path = data_root / f"global_briefing_replay-{start_date}-{end_date}.json"
    report_path = output_root / f"GLOBAL_BRIEFING_HISTORICAL_REPLAY-{start_date}-{end_date}.md"
    write_json_markdown(json_path, payload, report_path, build_replay_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(report_path)}


def _write_isolated_replay_ledger(
    data_root,
    replay_id: str,
    rows: list[dict[str, Any]],
    *,
    start_date: str,
    end_date: str,
    initial_cash: float,
) -> dict[str, str]:
    orders_path = data_root / "orders" / f"orders-{replay_id}.jsonl"
    trades_path = data_root / "trades" / f"trades-{replay_id}.jsonl"
    portfolio_path = data_root / "portfolio" / f"portfolio-{replay_id}.jsonl"
    account_path = data_root / "accounts" / f"account-{replay_id}.json"

    write_jsonl(orders_path, [{"replay_id": replay_id, "artifact_type": "orders", "rows": []}])
    write_jsonl(trades_path, [{"replay_id": replay_id, "artifact_type": "trades", "rows": []}])
    write_jsonl(
        portfolio_path,
        [
            {
                "replay_id": replay_id,
                "date": str(row.get("replay_date")),
                "cash": initial_cash,
                "market_value": 0.0,
                "total_asset": initial_cash,
                "positions": [],
                "source": "global_briefing_historical_no_trade_replay",
            }
            for row in rows
        ],
    )
    write_json(
        account_path,
        {
            "replay_id": replay_id,
            "start_date": start_date,
            "end_date": end_date,
            "cash": initial_cash,
            "total_asset": initial_cash,
            "isolated": True,
        },
    )
    return {
        "orders": str(orders_path),
        "trades": str(trades_path),
        "portfolio": str(portfolio_path),
        "account": str(account_path),
    }


def build_replay_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Global Briefing Historical Replay",
            "",
            "## Scope",
            "This is isolated historical replay.",
            "It is not forward dry-run.",
            "It is not live trading validation.",
            "It does not prove strategy effectiveness.",
            "",
            "## Inputs",
            f"- bundle={payload['input_bundle']}",
            f"- prices={payload['input_prices']}",
            "",
            "## Replay Summary",
            f"- replay_days={payload['summary']['replay_days']}",
            f"- days_processed={payload['summary']['days_processed']}",
            f"- orders={payload['summary']['orders']}",
            f"- trades={payload['summary']['trades']}",
            f"- ending_equity={payload['summary']['ending_equity']}",
            f"- warnings={payload['warnings']}",
            "",
            "## Data Quality",
            f"- missing_price_days={payload['data_quality']['missing_price_days']}",
            f"- missing_signal_days={payload['data_quality']['missing_signal_days']}",
            "",
            "## Isolated Output Paths",
            *[f"- {name}: {path}" for name, path in payload["isolated_output_paths"].items()],
            "",
            "## Boundary",
            "- isolated replay only",
            "- main ledger not written",
            "- run-daily CLI not called",
            "- no broker",
            "- no live trading",
            "- no labels",
            "- no ML shadow",
            "- no promotion",
            "",
        ]
    )
