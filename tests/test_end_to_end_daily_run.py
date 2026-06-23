from trading_core.daily_run import run_daily
from trading_core.storage.file_paths import project_paths
from trading_core.storage.jsonl_store import read_json, read_jsonl


def test_end_to_end_daily_run_generates_all_core_files(sample_workspace) -> None:
    result = run_daily("2026-06-23", sample_workspace)
    paths = project_paths(sample_workspace)

    assert result["trades"][0]["status"] == "filled"
    assert result["portfolio"]["positions"][0]["available_quantity"] == 0
    assert paths.dated_jsonl("signals", "trading_signals", "2026-06-23").exists()
    assert paths.dated_jsonl("orders", "orders", "2026-06-23").exists()
    assert paths.dated_jsonl("trades", "trades", "2026-06-23").exists()
    assert paths.dated_json("portfolios", "portfolio", "2026-06-23").exists()
    assert paths.dated_jsonl("valuations", "valuations", "2026-06-23").exists()
    assert paths.dated_json("benchmarks", "benchmark", "2026-06-23").exists()
    assert paths.dated_json("attribution", "attribution", "2026-06-23").exists()
    assert (paths.data_dir / "evolution" / "signal_scorecard-2026-06-23.json").exists()
    assert (paths.data_dir / "evolution" / "mistakes-2026-06-23.jsonl").exists()
    assert (paths.data_dir / "evolution" / "strategy_scorecard-2026-06-23.json").exists()
    assert (paths.data_dir / "evolution" / "rule_memory.json").exists()
    assert (paths.data_dir / "experiments" / "experiment_queue.jsonl").exists()
    assert paths.daily_report("2026-06-23").exists()

    assert read_jsonl(paths.dated_jsonl("signals", "trading_signals", "2026-06-23"))
    assert read_json(paths.dated_json("portfolios", "portfolio", "2026-06-23"))["total_asset"] > 0


def test_next_day_settles_t_plus_one(sample_workspace) -> None:
    run_daily("2026-06-23", sample_workspace)
    result = run_daily("2026-06-24", sample_workspace)
    assert result["portfolio"]["positions"][0]["available_quantity"] >= 1200
