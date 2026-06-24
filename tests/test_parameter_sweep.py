"""Tests for parameter sweep runner."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import pytest

from trading_core.experiments.parameter_sweep import (
    ParameterSweepValidationError,
    build_sweep_markdown,
    calculate_score,
    expand_parameter_grid,
    load_price_data,
    run_momentum_sweep_evaluator,
    run_parameter_sweep,
    save_sweep_json,
    save_sweep_markdown,
    validate_sweep_config,
)
from trading_core.storage.file_paths import ProjectPaths


# Sample config for testing
SAMPLE_SWEEP_CONFIG: dict[str, Any] = {
    "experiment_id": "EXP-sweep-test-20260624",
    "strategy_id": "momentum_strategy_v1",
    "mode": "shadow",
    "data_path": "data/raw/prices/etf_daily",
    "start_date": "2024-01-01",
    "end_date": "2024-03-01",
    "parameters": {
        "lookback_days": [5, 10],
        "top_k": [1, 2],
        "target_weight": [0.05],
    },
    "constraints": {
        "write_main_ledger": False,
        "allow_active": False,
        "shadow_only": True,
    },
}


@pytest.fixture
def sweep_paths(tmp_path: Path) -> ProjectPaths:
    """Create a temporary workspace for sweep tests."""
    workspace = tmp_path / "workspace"
    project_root = workspace / "work" / "trading-core"

    # Create directory structure
    (project_root / "data" / "raw" / "prices" / "etf_daily").mkdir(parents=True)
    (project_root / "data" / "experiments").mkdir(parents=True)
    (project_root / "outputs" / "experiments").mkdir(parents=True)

    # Create sample price data
    data_dir = project_root / "data" / "raw" / "prices" / "etf_daily"
    _create_sample_price_data(data_dir)

    return ProjectPaths(workspace_root=workspace)


def _create_sample_price_data(data_dir: Path) -> None:
    """Create sample CSV price data for testing."""
    # Create 3 ETFs with 60 days of data
    symbols = ["510300.SH", "159915.SZ", "512480.SH"]

    base_prices = {
        "510300.SH": 3.5,
        "159915.SZ": 2.0,
        "512480.SH": 1.2,
    }

    # Generate 60 trading days
    for symbol in symbols:
        rows = []
        price = base_prices[symbol]
        for day in range(60):
            date = f"2024-01-{day + 1:02d}"
            # Simple random walk with slight upward trend
            import random
            random.seed(day + hash(symbol) % 1000)
            change = random.uniform(-0.02, 0.025)
            price = price * (1 + change)
            rows.append({
                "date": date,
                "symbol": symbol,
                "open": round(price * 0.995, 4),
                "high": round(price * 1.01, 4),
                "low": round(price * 0.99, 4),
                "close": round(price, 4),
                "volume": 1000000 + day * 1000,
                "source": "test",
                "quality": "fresh",
            })

        csv_path = data_dir / f"{symbol}.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)


class TestParameterGridExpansion:
    """Tests for parameter grid expansion."""

    def test_expand_simple_grid(self) -> None:
        """Test basic parameter grid expansion."""
        params = {
            "lookback_days": [5, 10, 20],
            "top_k": [1, 2],
        }
        grid = expand_parameter_grid(params)
        assert len(grid) == 6  # 3 * 2

        # Check all combinations exist
        combinations = set()
        for g in grid:
            combinations.add((g["lookback_days"], g["top_k"]))

        expected = {(5, 1), (5, 2), (10, 1), (10, 2), (20, 1), (20, 2)}
        assert combinations == expected

    def test_expand_single_parameter(self) -> None:
        """Test grid with single parameter list."""
        params = {"lookback_days": [5, 10, 20]}
        grid = expand_parameter_grid(params)
        assert len(grid) == 3
        assert grid[0]["lookback_days"] == 5
        assert grid[2]["lookback_days"] == 20

    def test_expand_empty_parameters(self) -> None:
        """Test empty parameters returns single empty dict."""
        grid = expand_parameter_grid({})
        assert len(grid) == 1
        assert grid[0] == {}


class TestValidation:
    """Tests for sweep configuration validation."""

    def test_valid_config_passes(self) -> None:
        """Test that valid config passes validation."""
        validate_sweep_config(SAMPLE_SWEEP_CONFIG)  # Should not raise

    def test_allow_active_true_rejected(self) -> None:
        """Test that allow_active=true is rejected."""
        bad_config = {
            **SAMPLE_SWEEP_CONFIG,
            "constraints": {**SAMPLE_SWEEP_CONFIG["constraints"], "allow_active": True},
        }
        with pytest.raises(ParameterSweepValidationError, match="allow_active"):
            validate_sweep_config(bad_config)

    def test_write_main_ledger_true_rejected(self) -> None:
        """Test that write_main_ledger=true is rejected."""
        bad_config = {
            **SAMPLE_SWEEP_CONFIG,
            "constraints": {**SAMPLE_SWEEP_CONFIG["constraints"], "write_main_ledger": True},
        }
        with pytest.raises(ParameterSweepValidationError, match="write_main_ledger"):
            validate_sweep_config(bad_config)

    def test_shadow_only_false_rejected(self) -> None:
        """Test that shadow_only=false is rejected."""
        bad_config = {
            **SAMPLE_SWEEP_CONFIG,
            "constraints": {**SAMPLE_SWEEP_CONFIG["constraints"], "shadow_only": False},
        }
        with pytest.raises(ParameterSweepValidationError, match="shadow_only"):
            validate_sweep_config(bad_config)

    def test_mode_live_rejected(self) -> None:
        """Test that mode=live is rejected."""
        bad_config = {**SAMPLE_SWEEP_CONFIG, "mode": "live"}
        with pytest.raises(ParameterSweepValidationError, match="mode"):
            validate_sweep_config(bad_config)

    def test_wrong_strategy_id_rejected(self) -> None:
        """Test that wrong strategy_id is rejected."""
        bad_config = {**SAMPLE_SWEEP_CONFIG, "strategy_id": "some_other_strategy"}
        with pytest.raises(ParameterSweepValidationError, match="strategy_id"):
            validate_sweep_config(bad_config)

    def test_target_weight_too_high_rejected(self) -> None:
        """Test that target_weight > 0.20 is rejected."""
        bad_config = {
            **SAMPLE_SWEEP_CONFIG,
            "parameters": {
                **SAMPLE_SWEEP_CONFIG["parameters"],
                "target_weight": [0.25],
            },
        }
        with pytest.raises(ParameterSweepValidationError, match="target_weight"):
            validate_sweep_config(bad_config)

    def test_too_many_combinations_rejected(self) -> None:
        """Test that parameter grid > 500 is rejected."""
        bad_config = {
            **SAMPLE_SWEEP_CONFIG,
            "parameters": {
                "lookback_days": list(range(1, 101)),  # 100 values
                "top_k": list(range(1, 11)),  # 10 values
                "target_weight": [0.05],
            },
        }
        with pytest.raises(ParameterSweepValidationError, match="exceeds maximum"):
            validate_sweep_config(bad_config)

    def test_strategy_id_with_forbidden_keyword_rejected(self) -> None:
        """Test that strategy_id with forbidden keyword is rejected."""
        bad_config = {**SAMPLE_SWEEP_CONFIG, "strategy_id": "broker_momentum_v1"}
        with pytest.raises(ParameterSweepValidationError, match="forbidden keyword"):
            validate_sweep_config(bad_config)


class TestScoreCalculation:
    """Tests for heuristic score calculation."""

    def test_score_positive_excess(self) -> None:
        """Test score with positive excess return."""
        metrics = {
            "excess_return_vs_equal_etf": 0.05,
            "max_drawdown": 0.02,
            "turnover": 0.1,
            "cost_ratio": 0.001,
        }
        score = calculate_score(metrics)
        # 0.05*100 - 0.02*50 - 0.1*5 - 0.001*10 = 5 - 1 - 0.5 - 0.01 = 3.49
        assert score == pytest.approx(3.49, rel=0.01)

    def test_score_negative_excess(self) -> None:
        """Test score with negative excess return."""
        metrics = {
            "excess_return_vs_equal_etf": -0.05,
            "max_drawdown": 0.10,
            "turnover": 0.5,
            "cost_ratio": 0.005,
        }
        score = calculate_score(metrics)
        assert score < 0


class TestPriceDataLoading:
    """Tests for price data loading."""

    def test_load_price_data(self, sweep_paths: ProjectPaths) -> None:
        """Test loading price data from CSV files."""
        data_path = sweep_paths.data_dir / "raw" / "prices" / "etf_daily"
        prices = load_price_data(data_path)

        assert len(prices) == 3  # 3 ETFs
        assert "510300.SH" in prices
        assert "159915.SZ" in prices

        # Check data structure
        for symbol, rows in prices.items():
            assert len(rows) == 60  # 60 days
            assert "date" in rows[0]
            assert "close" in rows[0]
            assert rows[0]["date"] < rows[-1]["date"]  # Sorted


class TestMomentumSweepEvaluator:
    """Tests for the approximate shadow evaluator."""

    def test_evaluator_runs(self, sweep_paths: ProjectPaths) -> None:
        """Test that evaluator runs without errors."""
        data_path = sweep_paths.data_dir / "raw" / "prices" / "etf_daily"
        prices = load_price_data(data_path)

        params = {
            "lookback_days": 10,
            "top_k": 2,
            "target_weight": 0.05,
        }

        result = run_momentum_sweep_evaluator(prices, params)

        assert "total_return" in result
        assert "excess_return_vs_equal_etf" in result
        assert "max_drawdown" in result
        assert "trade_count" in result
        assert "turnover" in result
        assert "cost_total" in result
        assert "cost_ratio" in result

        # Max drawdown should be non-negative
        assert result["max_drawdown"] >= 0.0

    def test_evaluator_different_params(self, sweep_paths: ProjectPaths) -> None:
        """Test that different parameters give different results."""
        data_path = sweep_paths.data_dir / "raw" / "prices" / "etf_daily"
        prices = load_price_data(data_path)

        params1 = {"lookback_days": 5, "top_k": 1, "target_weight": 0.05}
        params2 = {"lookback_days": 20, "top_k": 3, "target_weight": 0.05}

        result1 = run_momentum_sweep_evaluator(prices, params1)
        result2 = run_momentum_sweep_evaluator(prices, params2)

        # Results should differ (at least trade count or turnover)
        assert result1["trade_count"] != result2["trade_count"] or \
               result1["turnover"] != result2["turnover"]


class TestParameterSweep:
    """Tests for full parameter sweep."""

    def test_sweep_generates_json(self, sweep_paths: ProjectPaths) -> None:
        """Test that sweep generates JSON output."""
        config = {
            **SAMPLE_SWEEP_CONFIG,
            "data_path": str(sweep_paths.data_dir / "raw" / "prices" / "etf_daily"),
        }

        result = run_parameter_sweep(config, sweep_paths)

        assert result["experiment_id"] == "EXP-sweep-test-20260624"
        assert result["strategy_id"] == "momentum_strategy_v1"
        assert result["parameter_grid_size"] == 4  # 2 * 2 * 1
        assert len(result["runs"]) == 4

        # Check run structure
        for run in result["runs"]:
            assert "run_id" in run
            assert "parameters" in run
            assert "score" in run
            assert "status" in run
            assert run["status"] == "shadow_result"

    def test_sweep_saves_json(self, sweep_paths: ProjectPaths) -> None:
        """Test that sweep JSON is saved to file."""
        config = {
            **SAMPLE_SWEEP_CONFIG,
            "data_path": str(sweep_paths.data_dir / "raw" / "prices" / "etf_daily"),
        }

        result = run_parameter_sweep(config, sweep_paths)
        json_path = save_sweep_json(result, sweep_paths)

        assert json_path.exists()
        assert json_path.name == "parameter_sweep-EXP-sweep-test-20260624.json"
        assert json_path.parent.name == "experiments"

    def test_sweep_generates_markdown(self, sweep_paths: ProjectPaths) -> None:
        """Test that sweep generates markdown report."""
        config = {
            **SAMPLE_SWEEP_CONFIG,
            "data_path": str(sweep_paths.data_dir / "raw" / "prices" / "etf_daily"),
        }

        result = run_parameter_sweep(config, sweep_paths)
        md_path = save_sweep_markdown(result, sweep_paths)

        assert md_path.exists()
        content = md_path.read_text(encoding="utf-8")

        # Check required sections
        assert "# Parameter Sweep Report" in content
        assert "Safety Boundary" in content
        assert "shadow_only: true" in content
        assert "write_main_ledger: false" in content
        assert "allow_active: false" in content
        assert "No orders/trades/portfolio written" in content
        assert "Not active" in content
        assert "Not an admission gate" in content
        assert "Method" in content
        assert "approximate shadow evaluator" in content
        assert "heuristic score only" in content
        assert "Results" in content
        assert "Limitations" in content
        assert "Not a formal backtest" in content
        assert "Not sufficient for promotion" in content

    def test_best_shadow_candidate_not_active(self, sweep_paths: ProjectPaths) -> None:
        """Test that best candidate is not marked as active."""
        config = {
            **SAMPLE_SWEEP_CONFIG,
            "data_path": str(sweep_paths.data_dir / "raw" / "prices" / "etf_daily"),
        }

        result = run_parameter_sweep(config, sweep_paths)
        best = result.get("best_shadow_candidate")

        if best is not None:
            # Should not have 'active' status
            assert "active" not in str(best).lower()
            # Key should be 'best_shadow_candidate', not 'best_active'
            assert "best_shadow_candidate" in result

    def test_no_orders_trades_portfolio_written(self, sweep_paths: ProjectPaths) -> None:
        """Test that sweep does not write orders/trades/portfolio files."""
        config = {
            **SAMPLE_SWEEP_CONFIG,
            "data_path": str(sweep_paths.data_dir / "raw" / "prices" / "etf_daily"),
        }

        run_parameter_sweep(config, sweep_paths)

        # These directories should not have new files
        for bucket in ["orders", "trades", "portfolios"]:
            data_dir = sweep_paths.data_dir / bucket
            if data_dir.exists():
                assert len(list(data_dir.glob("*"))) == 0, f"{bucket} should be empty"

    def test_report_contains_heuristic_score_only(self, sweep_paths: ProjectPaths) -> None:
        """Test that report contains 'heuristic score only'."""
        config = {
            **SAMPLE_SWEEP_CONFIG,
            "data_path": str(sweep_paths.data_dir / "raw" / "prices" / "etf_daily"),
        }

        result = run_parameter_sweep(config, sweep_paths)
        md = build_sweep_markdown(result)

        assert "heuristic score only" in md

    def test_report_contains_not_admission_gate(self, sweep_paths: ProjectPaths) -> None:
        """Test that report contains 'not an admission gate'."""
        config = {
            **SAMPLE_SWEEP_CONFIG,
            "data_path": str(sweep_paths.data_dir / "raw" / "prices" / "etf_daily"),
        }

        result = run_parameter_sweep(config, sweep_paths)
        md = build_sweep_markdown(result)

        assert "not an admission gate" in md

    def test_report_contains_no_orders_written(self, sweep_paths: ProjectPaths) -> None:
        """Test that report contains 'no orders/trades/portfolio written'."""
        config = {
            **SAMPLE_SWEEP_CONFIG,
            "data_path": str(sweep_paths.data_dir / "raw" / "prices" / "etf_daily"),
        }

        result = run_parameter_sweep(config, sweep_paths)
        md = build_sweep_markdown(result)

        assert "no orders/trades/portfolio written" in md.lower()


class TestCLISmoke:
    """Smoke tests for CLI integration."""

    def test_cli_smoke(self, sweep_paths: ProjectPaths, tmp_path: Path) -> None:
        """Test that CLI command can be invoked (basic smoke test)."""
        from trading_core.cli import main

        # Create a config file
        config_path = tmp_path / "sweep_config.yaml"
        import yaml
        config = {
            **SAMPLE_SWEEP_CONFIG,
            "data_path": str(sweep_paths.data_dir / "raw" / "prices" / "etf_daily"),
        }
        with open(config_path, "w") as f:
            yaml.dump(config, f)

        # Test CLI command
        result = main(["run-parameter-sweep", "--config", str(config_path)])

        # Should return 0 on success
        assert result == 0


class TestRealData:
    """Tests with real ETF data (if available)."""

    def test_real_data_available(self) -> None:
        """Check if real data directory exists."""
        # This test just checks if data exists, doesn't fail if not
        data_path = Path("work/trading-core/data/raw/prices/etf_daily")
        if data_path.exists():
            csv_files = list(data_path.glob("*.csv"))
            assert len(csv_files) > 0
        else:
            pytest.skip("Real data not available")
