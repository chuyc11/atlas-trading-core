from __future__ import annotations

from trading_core.signals.macro_signal_loader import sync_macro_signals
from trading_core.storage.file_paths import project_paths
from trading_core.storage.jsonl_store import read_jsonl, write_jsonl


def macro(date: str, scenario: str) -> dict[str, object]:
    return {
        "macro_signal_id": f"M-{date}",
        "date": date,
        "region": "CHINA",
        "theme": "test",
        "scenario": scenario,
        "confidence": "medium",
        "affected_assets": ["510300.SH"],
        "risk_flags": [],
        "status": "open",
    }


def test_sync_refreshes_a_stale_same_day_local_copy(tmp_path) -> None:
    date = "2026-07-10"
    paths = project_paths(tmp_path)
    source = paths.global_briefing_data_dir / f"macro_signals-{date}.jsonl"
    local = paths.data_dir / "macro_signals" / source.name
    write_jsonl(source, [macro(date, "revised upstream")])
    write_jsonl(local, [macro(date, "stale local")])

    rows, limitations = sync_macro_signals(date, paths)

    assert limitations == []
    assert rows[0]["scenario"] == "revised upstream"
    assert read_jsonl(local) == read_jsonl(source)
    assert local.read_bytes() == source.read_bytes()


def test_sync_dry_run_does_not_replace_local_copy(tmp_path) -> None:
    date = "2026-07-10"
    paths = project_paths(tmp_path)
    source = paths.global_briefing_data_dir / f"macro_signals-{date}.jsonl"
    local = paths.data_dir / "macro_signals" / source.name
    write_jsonl(source, [macro(date, "revised upstream")])
    write_jsonl(local, [macro(date, "stale local")])

    rows, limitations = sync_macro_signals(date, paths, write_local=False)

    assert limitations == []
    assert rows[0]["scenario"] == "revised upstream"
    assert read_jsonl(local)[0]["scenario"] == "stale local"


def test_sync_can_explicitly_accept_and_copy_an_empty_daily_export(tmp_path) -> None:
    date = "2026-07-22"
    paths = project_paths(tmp_path)
    source = paths.global_briefing_data_dir / f"macro_signals-{date}.jsonl"
    local = paths.data_dir / "macro_signals" / source.name
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text("", encoding="utf-8")
    write_jsonl(local, [macro(date, "stale local")])

    rows, limitations = sync_macro_signals(date, paths, allow_empty=True)

    assert rows == []
    assert limitations == [f"empty global macro_signals for {date}"]
    assert local.read_bytes() == source.read_bytes() == b""
