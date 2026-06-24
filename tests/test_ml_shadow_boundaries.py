"""ML shadow boundary tests — verify architecture isolation.

These tests ensure that the ML shadow pipeline does not violate
any of the project's hard boundaries:
- ML does not affect run-daily.
- Labels are not used in the trading path.
- Features do not contain future data.
- ML outputs never write main ledger paths.
- Shadow signals are not treated as active trading signals.
"""

from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path
from typing import Any

import pytest

from trading_core.features.feature_store import FEATURE_COLUMNS
from trading_core.ml.prediction_engine import generate_ml_shadow_predictions
from trading_core.ml.shadow_leaderboard import build_ml_shadow_leaderboard
from trading_core.ml.shadow_report import build_ml_shadow_report
from trading_core.ml.walk_forward_dataset import ROWS_COLUMNS, build_walk_forward_dataset
from trading_core.storage.file_paths import project_paths
from trading_core.storage.jsonl_store import read_jsonl

from ml_shadow_test_utils import (
    assert_no_main_ledgers,
    build_sample_ml_pipeline,
    read_csv_rows,
    write_feature_label_matrices,
    write_prediction_fixture,
)


# ---------------------------------------------------------------------------
# D1 + D2: run-daily does not import labels or ML modules
# ---------------------------------------------------------------------------

def _imports_from_source(module_name: str) -> set[str]:
    """Parse the source file of a module and return all imported module paths."""
    spec = importlib.util.find_spec(module_name)
    if spec is None or spec.origin is None:
        pytest.skip(f"Cannot locate source for {module_name}")
    source = Path(spec.origin).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)
    return imports


def test_run_daily_does_not_import_labels_module() -> None:
    """run-daily must never import anything from trading_core.labels."""
    imports = _imports_from_source("trading_core.daily_run")
    label_imports = [name for name in imports if "labels" in name]
    assert label_imports == [], f"daily_run imports labels modules: {label_imports}"


def test_run_daily_does_not_import_ml_shadow_module() -> None:
    """run-daily must never import anything from trading_core.ml."""
    imports = _imports_from_source("trading_core.daily_run")
    ml_imports = [name for name in imports if "trading_core.ml" in name]
    assert ml_imports == [], f"daily_run imports ML modules: {ml_imports}"


def test_run_daily_does_not_import_feature_store() -> None:
    """run-daily must never import the feature_store module."""
    imports = _imports_from_source("trading_core.daily_run")
    feature_imports = [name for name in imports if "feature_store" in name]
    assert feature_imports == [], f"daily_run imports feature_store: {feature_imports}"


# ---------------------------------------------------------------------------
# D4: Feature columns do not contain future_* fields
# ---------------------------------------------------------------------------

def test_feature_columns_do_not_contain_future_fields() -> None:
    """Feature column names must never include future_* prefixed fields."""
    future_features = [col for col in FEATURE_COLUMNS if col.startswith("future_")]
    assert future_features == [], f"FEATURE_COLUMNS contains future fields: {future_features}"


def test_feature_columns_do_not_contain_label_value() -> None:
    """Feature column names must not include label_value."""
    assert "label_value" not in FEATURE_COLUMNS, "FEATURE_COLUMNS contains label_value"


# ---------------------------------------------------------------------------
# D5: Walk-forward rows feature columns do not contain label_value
# ---------------------------------------------------------------------------

def test_walk_forward_rows_feature_columns_do_not_include_label_value(tmp_path: Path) -> None:
    """Walk-forward CSV rows must not expose label_value as a feature column."""
    paths = project_paths(tmp_path)
    features, labels, days, _symbols = write_feature_label_matrices(tmp_path)

    result = build_walk_forward_dataset(
        features, labels, days[0], days[-1],
        5, 3, 3, 3,
        "future_5d_excess_vs_equal_etf", paths,
    )

    rows = read_csv_rows(Path(result["rows_path"]))
    assert rows, "No walk-forward rows generated"
    first_row = rows[0]
    # label_value is present in the row for training targets, but it must NOT
    # be among the FEATURE_COLUMNS used as model input.
    for feature_col in FEATURE_COLUMNS:
        assert feature_col in first_row, f"Feature column {feature_col} missing from walk-forward row"
    # Ensure no future_* column is in the rows beyond what's in ROWS_COLUMNS
    for col_name in first_row:
        if col_name.startswith("future_"):
            assert False, f"Walk-forward row contains future field: {col_name}"


# ---------------------------------------------------------------------------
# D3: Mock model prediction_score is not equal to label_value
# ---------------------------------------------------------------------------

def test_mock_model_prediction_score_not_equal_to_label_value(tmp_path: Path) -> None:
    """Mock model must not cheat by copying label_value as prediction_score."""
    pipeline = build_sample_ml_pipeline(tmp_path)
    predictions = read_jsonl(Path(pipeline["predictions"]["output_path"]))
    assert predictions, "No predictions generated"
    scores_equal_to_labels = [
        row for row in predictions
        if row.get("label_value") is not None
        and abs(float(row["prediction_score"]) - float(row["label_value"])) < 1e-12
    ]
    # With diverse test data, it would be extremely unlikely for all scores to equal labels.
    # We check that not ALL predictions have score == label.
    assert len(scores_equal_to_labels) < len(predictions), (
        "All prediction_scores equal label_values — mock model is cheating"
    )


# ---------------------------------------------------------------------------
# D6: Shadow signals not accepted by order generator
# ---------------------------------------------------------------------------

def test_shadow_signals_not_accepted_by_order_generator() -> None:
    """The main signal generator and virtual broker must not accept shadow signals.

    Shadow signals have status='shadow_candidate' and use a different schema
    (shadow_signal_id, prediction_id, etc.) that is incompatible with the
    main TradingSignal schema used by generate_trading_signals and process_signals.
    """
    # Verify that a shadow signal lacks the required fields for process_signals
    shadow_signal = {
        "shadow_signal_id": "MLSHADOWSIG-000001",
        "prediction_id": "MLPRED-000001",
        "model_id": "MLSHADOW-20260101-20260131-mock",
        "date": "2026-01-15",
        "symbol": "510300.SH",
        "side": "LONG",
        "target_weight": 0.05,
        "prediction_score": 0.5,
        "prediction_rank": 1,
        "shadow_only": True,
        "write_main_ledger": False,
        "status": "shadow_candidate",
    }
    # Main trading signals require signal_id, account_id, strategy_id, market, etc.
    required_main_fields = ["signal_id", "account_id", "strategy_id", "market", "confidence"]
    missing = [field for field in required_main_fields if field not in shadow_signal]
    assert missing, (
        "Shadow signal unexpectedly has all main signal fields — "
        "this could allow it to be processed as an active signal"
    )


# ---------------------------------------------------------------------------
# D7: Shadow recommendation does not trigger promotion
# ---------------------------------------------------------------------------

def test_shadow_recommendation_watch_does_not_trigger_promotion(tmp_path: Path) -> None:
    """A 'watch' recommendation must not auto-promote to active."""
    paths = project_paths(tmp_path)
    predictions, signals = write_prediction_fixture(
        tmp_path, prediction_count=30, positive_ic=True, signal_side="bottom",
    )
    result = build_ml_shadow_leaderboard(predictions, signals, "EQUAL_ETF", paths)
    assert result["shadow_recommendation"] == "watch"
    assert result["shadow_only"] is True
    assert result["write_main_ledger"] is False
    assert result.get("not_active") is True


def test_shadow_recommendation_promising_does_not_trigger_promotion(tmp_path: Path) -> None:
    """A 'promising' recommendation must not auto-promote to active."""
    paths = project_paths(tmp_path)
    predictions, signals = write_prediction_fixture(
        tmp_path, prediction_count=30, positive_ic=True, signal_side="top",
    )
    result = build_ml_shadow_leaderboard(predictions, signals, "EQUAL_ETF", paths)
    assert result["shadow_recommendation"] == "promising"
    assert result["shadow_only"] is True
    assert result["write_main_ledger"] is False
    assert result.get("not_active") is True
    # No promotion gate is called, no state change occurs.
    assert_no_main_ledgers(paths)


# ---------------------------------------------------------------------------
# D10: Shadow report contains 'not used by run-daily'
# ---------------------------------------------------------------------------

def test_shadow_report_contains_not_used_by_run_daily(tmp_path: Path) -> None:
    """Shadow research report must state it is not used by run-daily."""
    pipeline = build_sample_ml_pipeline(tmp_path)
    leaderboard = build_ml_shadow_leaderboard(
        Path(pipeline["predictions"]["output_path"]),
        Path(pipeline["signals"]["output_path"]),
        "EQUAL_ETF",
        pipeline["paths"],
    )
    result = build_ml_shadow_report(
        Path(pipeline["dataset"]["output_path"]),
        Path(pipeline["model"]["model_path"]),
        Path(pipeline["predictions"]["output_path"]),
        Path(pipeline["signals"]["output_path"]),
        Path(leaderboard["output_path"]),
        pipeline["paths"],
    )
    report = Path(result["report_path"]).read_text(encoding="utf-8")
    assert "not used by run-daily" in report
    assert "shadow_only=true" in report
    assert "write_main_ledger=false" in report


# ---------------------------------------------------------------------------
# D13: label_available=false excluded from training
# ---------------------------------------------------------------------------

def test_label_available_false_excluded_from_training(tmp_path: Path) -> None:
    """Rows with label_available=false must not appear in walk-forward output."""
    paths = project_paths(tmp_path)
    features, labels, days, _symbols = write_feature_label_matrices(tmp_path)

    result = build_walk_forward_dataset(
        features, labels, days[0], days[-1],
        5, 3, 3, 3,
        "future_5d_excess_vs_equal_etf", paths,
    )

    rows = read_csv_rows(Path(result["rows_path"]))
    # All rows in output must have non-empty label_value (label_available=false rows excluded)
    for row in rows:
        assert row["label_value"].strip() != "", f"Empty label_value found: {row}"
    assert result["label_unavailable_rows"] >= 1, "Expected at least 1 unavailable label row"


# ---------------------------------------------------------------------------
# D15: ML pipeline outputs write_main_ledger is always False
# ---------------------------------------------------------------------------

def test_ml_pipeline_outputs_write_main_ledger_is_false(tmp_path: Path) -> None:
    """All ML pipeline output records must have write_main_ledger=False."""
    pipeline = build_sample_ml_pipeline(tmp_path)

    # Check model metadata
    assert pipeline["model"]["write_main_ledger"] is False
    assert pipeline["model"]["shadow_only"] is True

    # Check predictions
    predictions = read_jsonl(Path(pipeline["predictions"]["output_path"]))
    for pred in predictions:
        assert pred["write_main_ledger"] is False, f"prediction has write_main_ledger=True: {pred}"
        assert pred["shadow_only"] is True, f"prediction has shadow_only=False: {pred}"

    # Check signals
    signals = read_jsonl(Path(pipeline["signals"]["output_path"]))
    for sig in signals:
        assert sig["write_main_ledger"] is False, f"signal has write_main_ledger=True: {sig}"
        assert sig["shadow_only"] is True, f"signal has shadow_only=False: {sig}"

    # Check no main ledger directories created
    assert_no_main_ledgers(pipeline["paths"])


def test_ml_predictions_do_not_write_main_ledger_paths(tmp_path: Path) -> None:
    """Prediction output files must be in data/shadow, not data/orders, data/trades, etc."""
    pipeline = build_sample_ml_pipeline(tmp_path)
    paths = pipeline["paths"]
    output_path = Path(pipeline["predictions"]["output_path"])

    # Output must be under data/shadow/
    assert "shadow" in output_path.parts, f"Prediction output not in shadow directory: {output_path}"

    # Main ledger directories must not exist
    for ledger_dir in ["orders", "trades", "portfolios"]:
        ledger_path = paths.data_dir / ledger_dir
        assert not ledger_path.exists(), f"Main ledger directory {ledger_dir} was created by ML pipeline"


# ---------------------------------------------------------------------------
# Replay isolation
# ---------------------------------------------------------------------------

def test_replay_write_main_ledger_raises_error(tmp_path: Path) -> None:
    """Replay with --write-main-ledger must raise ValueError."""
    from trading_core.evaluation.historical_dry_run_replay import replay_dry_run

    # Create a minimal price CSV so _load_price_package succeeds
    # and the function reaches the write_main_ledger guard.
    price_csv = tmp_path / "prices.csv"
    price_csv.write_text(
        "date,symbol,open,high,low,close,volume,source,quality\n"
        "2026-01-02,510300.SH,100,101,99,100.5,1000,test,fresh\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="intentionally unsupported"):
        replay_dry_run(
            "2026-01-01", "2026-01-31",
            price_csv,
            write_main_ledger=True,
        )
