"""Point-in-time global-briefing replay bundle builder."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path
from typing import Any

from trading_core.global_briefing.signal_schema import (
    DEFAULT_DECISION_TIME,
    compact_date,
    decision_timestamp,
    generated_sort_key,
    normalize_datetime,
    parse_datetime,
    read_signal_package,
    resolve_project_path,
    validate_signal_row,
)
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, write_json_markdown


def build_global_briefing_replay_bundle(
    signals_path: str,
    prices_path: str,
    *,
    start_date: str,
    end_date: str,
    decision_time: str = DEFAULT_DECISION_TIME,
    allow_carry_forward: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    signal_rows = _load_valid_signal_rows(signals_path, paths)
    price_dates = _load_price_dates(prices_path, start_date, end_date, paths)
    if not price_dates:
        raise ValueError("price dates missing for requested replay range")

    rows: list[dict[str, Any]] = []
    missing_signal_days: list[str] = []
    carry_forward_days_used: list[dict[str, Any]] = []
    violations: list[str] = []

    for replay_date in price_dates:
        selected = _select_signal_for_date(signal_rows, replay_date, decision_time, allow_carry_forward)
        if selected is None:
            missing_signal_days.append(replay_date)
            rows.append(
                {
                    "replay_date": replay_date,
                    "selected_signal_as_of_date": None,
                    "selected_signal_generated_at": None,
                    "selected_signal_source": None,
                    "selected_signal_version": None,
                    "carry_forward_days": None,
                    "signals": {},
                }
            )
            continue
        generated_dt, _warnings = parse_datetime(selected["generated_at"])
        decision_dt = decision_timestamp(replay_date, decision_time)
        carry_days = (date.fromisoformat(replay_date) - date.fromisoformat(selected["as_of_date"])).days
        if generated_dt is None or normalize_datetime(generated_dt) > decision_dt:
            violations.append(f"{replay_date}: selected generated_at after decision timestamp")
        if selected["as_of_date"] > replay_date:
            violations.append(f"{replay_date}: selected future as_of_date")
        if carry_days > 0:
            carry_forward_days_used.append(
                {
                    "replay_date": replay_date,
                    "selected_signal_as_of_date": selected["as_of_date"],
                    "carry_forward_days": carry_days,
                }
            )
        rows.append(
            {
                "replay_date": replay_date,
                "selected_signal_as_of_date": selected["as_of_date"],
                "selected_signal_generated_at": selected["generated_at"],
                "selected_signal_source": selected.get("source"),
                "selected_signal_version": selected.get("version"),
                "carry_forward_days": carry_days,
                "signals": selected.get("signals", {}),
            }
        )

    bundle_id = f"GB-REPLAY-BUNDLE-{compact_date(start_date)}-{compact_date(end_date)}"
    payload: dict[str, Any] = {
        "bundle_id": bundle_id,
        "start_date": start_date,
        "end_date": end_date,
        "decision_time": decision_time,
        "allow_carry_forward": allow_carry_forward,
        "input_signals": str(resolve_project_path(signals_path, paths)),
        "input_prices": str(resolve_project_path(prices_path, paths)),
        "rows": rows,
        "coverage": {
            "replay_days": len(rows),
            "days_with_signal": len([row for row in rows if row["selected_signal_generated_at"]]),
            "missing_signal_days": missing_signal_days,
        },
        "carry_forward": {
            "used": bool(carry_forward_days_used),
            "days": carry_forward_days_used,
        },
        "point_in_time": {
            "future_signal_used": bool(violations),
            "violations": violations,
        },
        "boundary": {
            "bundle_only": True,
            "trading_signal": False,
            "orders_written": False,
            "trades_written": False,
            "portfolio_written": False,
            "accounts_written": False,
            "run_daily_called": False,
        },
    }
    json_path = paths.data_dir / "replays" / "global_briefing" / f"replay_bundle-{start_date}-{end_date}.json"
    report_path = paths.outputs_dir / "replays" / "global_briefing" / f"GLOBAL_BRIEFING_REPLAY_BUNDLE-{start_date}-{end_date}.md"
    write_json_markdown(json_path, payload, report_path, build_bundle_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(report_path)}


def _load_valid_signal_rows(signals_path: str, paths: ProjectPaths) -> list[dict[str, Any]]:
    package = read_signal_package(signals_path, paths)
    blocking = list(package.blocking_reasons)
    rows: list[dict[str, Any]] = []
    for row_number, row in enumerate(package.rows, 1):
        clean, row_blocking, _warnings = validate_signal_row(row, row_number, check_point_in_time=False)
        if row_blocking:
            blocking.extend(row_blocking)
        elif clean is not None:
            rows.append(clean)
    if blocking:
        raise ValueError("; ".join(blocking))
    if not rows:
        raise ValueError("signal rows missing for replay bundle")
    return rows


def _load_price_dates(prices_path: str, start_date: str, end_date: str, paths: ProjectPaths) -> list[str]:
    path = resolve_project_path(prices_path, paths)
    if not path.exists():
        raise ValueError(f"prices file missing: {path}")
    files = sorted(path.glob("*.csv")) if path.is_dir() else [path]
    dates: set[str] = set()
    for file_path in files:
        with file_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames or "date" not in reader.fieldnames:
                raise ValueError(f"prices file missing date column: {file_path}")
            for row in reader:
                day = str(row.get("date", "")).strip()
                if start_date <= day <= end_date:
                    dates.add(day)
    return sorted(dates)


def _select_signal_for_date(
    rows: list[dict[str, Any]],
    replay_date: str,
    decision_time: str,
    allow_carry_forward: bool,
) -> dict[str, Any] | None:
    decision_dt = decision_timestamp(replay_date, decision_time)

    def eligible(row: dict[str, Any]) -> bool:
        generated_dt, _warnings = parse_datetime(row.get("generated_at"))
        return generated_dt is not None and normalize_datetime(generated_dt) <= decision_dt and row["as_of_date"] <= replay_date

    same_day = [row for row in rows if row["as_of_date"] == replay_date and eligible(row)]
    if same_day:
        return max(same_day, key=generated_sort_key)
    if not allow_carry_forward:
        return None
    carried = [row for row in rows if row["as_of_date"] < replay_date and eligible(row)]
    if not carried:
        return None
    return max(carried, key=lambda row: (row["as_of_date"], generated_sort_key(row)))


def build_bundle_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Global Briefing Replay Bundle",
            "",
            "## Scope",
            "This bundle is macro input for isolated historical replay.",
            "It is not a trading signal.",
            "",
            "## Coverage",
            f"- replay_days={payload['coverage']['replay_days']}",
            f"- days_with_signal={payload['coverage']['days_with_signal']}",
            "",
            "## Missing Signal Days",
            *([f"- {day}" for day in payload["coverage"]["missing_signal_days"]] if payload["coverage"]["missing_signal_days"] else ["- none"]),
            "",
            "## Carry-Forward Use",
            *(
                [
                    f"- {item['replay_date']}: {item['selected_signal_as_of_date']} ({item['carry_forward_days']} days)"
                    for item in payload["carry_forward"]["days"]
                ]
                if payload["carry_forward"]["days"]
                else ["- none"]
            ),
            "",
            "## Point-in-Time Safety",
            f"- future_signal_used={str(payload['point_in_time']['future_signal_used']).lower()}",
            f"- violations={payload['point_in_time']['violations']}",
            "",
            "## Boundary",
            "- bundle only",
            "- no orders",
            "- no trades",
            "- no portfolio",
            "- no run-daily",
            "",
        ]
    )
