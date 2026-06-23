from trading_core.backtest.walk_forward import run_walk_forward


def test_walk_forward_runs_windows(sample_workspace) -> None:
    summary = run_walk_forward("2026-06-23", "2026-06-24", window_days=1, workspace_root=sample_workspace)
    assert len(summary["windows"]) == 2
    assert summary["strategy_scope"] == "first-stage rule strategies only"
