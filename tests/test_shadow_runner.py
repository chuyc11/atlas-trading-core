from trading_core.evolution.shadow_runner import run_shadow
from trading_core.storage.file_paths import project_paths


def test_shadow_runner_records_without_main_portfolio(sample_workspace) -> None:
    rows = run_shadow(
        "2026-06-23",
        "CHINA_PAPER",
        {"510300.SH": {"price": 4.0, "change_pct": 1.0, "raw": {"market": "A_SHARE"}}},
        paths=project_paths(sample_workspace),
    )
    assert rows[0]["status"] == "shadow"
