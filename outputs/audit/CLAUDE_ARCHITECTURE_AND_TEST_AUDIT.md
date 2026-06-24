# Claude Architecture and Test Audit

**Audit date**: 2026-06-24
**HEAD**: 2396745 feat: add ML shadow research pipeline v1
**Baseline**: python -m pytest → 173 passed

---

## 1. Summary

- **No critical boundary violation found.** The ML shadow pipeline is cleanly isolated from the main trading pipeline.
- `daily_run.py` imports zero modules from `ml/`, `labels/`, or `features/` — the firewall is intact.
- `label_store` is never read by `run-daily`, `signal_generator`, or `virtual_broker`.
- All features (`return_5d`, `return_20d`, `volatility_20d`, `drawdown_20d`) use past-only lookback windows — no future data leakage.
- Walk-forward dataset builder enforces strict temporal splits with `_leakage_check()`.
- Mock model `_mock_score()` uses feature columns only (`return_1d/5d/20d`, `drawdown_20d`) — it does **not** read `label_value`.
- All ML outputs write to `data/ml/`, `data/shadow/`, `outputs/ml/`, `outputs/shadow/` — zero writes to main ledger paths.
- Replay module uses `ReplayPaths` with `data/replays/` namespace; `--write-main-ledger` raises `ValueError`.
- Historical replay hardcodes `forward_30d_dry_run_passed: False` — no misrepresentation.
- Shadow research report clearly states: `shadow_only=true`, `write_main_ledger=false`, `not used by run-daily`, `mock model is for pipeline validation only`.

---

## 2. Critical Risks

**No critical boundary violation found.**

| risk_id | severity | file | description | evidence | recommended_fix |
|---------|----------|------|-------------|----------|-----------------|
| — | — | — | No critical risks identified | — | — |

---

## 3. Data Leakage Review

### Feature Leakage Status: ✅ PASS

| Feature | Method | Leakage Risk |
|---------|--------|-------------|
| `return_1d` | `_return_from(closes, index, 1)` — lookback 1 | None |
| `return_5d` | `_return_from(closes, index, 5)` — lookback 5 | None |
| `return_20d` | `_return_from(closes, index, 20)` — lookback 20 | None |
| `volatility_20d` | `_volatility(daily_returns, index, 20)` — past 20-day window | None |
| `volume_change_5d` | `_return_from(volumes, index, 5)` — lookback 5 | None |
| `drawdown_20d` | `_drawdown(values, index, 20)` — past 20-day window | None |
| `ma_5`, `ma_20` | `_moving_average(closes, index, window)` — `values[index - window + 1 : index + 1]` | None |
| `price_above_ma20` | `current close > ma_20` — current day only | None |

- `_return_from()` at `feature_store.py:147-153`: `if index < lookback: return None; return (values[index] / values[index - lookback]) - 1`
- `_moving_average()` at `feature_store.py:156-159`: window uses `values[index - window + 1 : index + 1]`
- `_volatility()` at `feature_store.py:162-168`: window uses `daily_returns[index - window + 1 : index + 1]`
- `_drawdown()` at `feature_store.py:171-178`: window uses `values[index - window + 1 : index + 1]`

### Label Leakage Status: ✅ PASS

- Labels use `_future_return(values, index, horizon)` at `label_store.py:136-143` — accesses `values[index + horizon]` (future).
- This is explicitly by design for offline labels.
- `label_store.py:64-66`: `leakage_policy: "offline labels use future data by design; labels must not be used in run-daily decision path"`.
- `label_store.py:67`: `offline_only: True`.
- `daily_run.py` does NOT import `label_store` — verified.

### Dataset Split Status: ✅ PASS

- `walk_forward_dataset.py:190-224`: `_build_windows()` constructs splits as contiguous, non-overlapping date ranges.
- `_leakage_check()` at `walk_forward_dataset.py:265-272` validates:
  - `train_end < validation_start`
  - `validation_end < test_start`
- `_split_for_date()` at `walk_forward_dataset.py:255-262` assigns rows to exactly one split.

### Model Training Leakage Status: ✅ PASS

- `prediction_engine.py:71-77` — `_mock_score()` computes: `3.0 * return_20d + 2.0 * return_5d + 1.0 * return_1d - 0.5 * |drawdown_20d|`
- Uses ONLY feature columns (`return_20d`, `return_5d`, `return_1d`, `drawdown_20d`).
- Does NOT access `label_value`, `future_*_return`, or any label column.

### Prediction/Evaluation Separation Status: ✅ PASS

- `prediction_engine.py:27`: `scored = [{**row, "prediction_score": _mock_score(row)} for row in test_rows]`
- Score computed from features only.
- `prediction_engine.py:45`: `label_value` is included in output for evaluation purposes but is NOT used in scoring.
- `shadow_leaderboard.py` reads `label_value` only for rank IC and hit rate evaluation — does not feed back into prediction scores.
- `shadow_report.py` aggregates existing artifacts — no score recalculation.

---

## 4. Main Ledger Pollution Review

| # | CLI Command | Write Paths | Main Ledger Write? | Verdict |
|---|-------------|-------------|-------------------|---------|
| C1 | `build-features` | `data/features/`, `outputs/features/` | No | ✅ PASS |
| C2 | `build-labels` | `data/labels/`, `outputs/labels/` | No | ✅ PASS |
| C3 | `build-ml-dataset` | `data/ml/datasets/`, `outputs/ml/datasets/` | No | ✅ PASS |
| C4 | `train-ml-shadow` | `data/ml/models/`, `outputs/ml/models/` | No | ✅ PASS |
| C5 | `predict-ml-shadow` | `data/shadow/`, `outputs/shadow/` | No | ✅ PASS |
| C6 | `generate-ml-shadow-signals` | `data/shadow/`, `outputs/shadow/` | No | ✅ PASS |
| C7 | `ml-shadow-leaderboard` | `data/shadow/`, `outputs/shadow/` | No | ✅ PASS |
| C8 | `ml-shadow-report` | `data/shadow/`, `outputs/shadow/` | No | ✅ PASS |
| C9 | `replay-dry-run` | `data/replays/{id}/`, `outputs/replays/{id}/` | No (`write_main_ledger` raises ValueError) | ✅ PASS |
| C10 | `replay-last-trading-days` | same as C9 | No | ✅ PASS |

**Evidence**: All ML modules set `shadow_only: True` and `write_main_ledger: False` in their output metadata.

**Existing test coverage**: `assert_no_main_ledgers()` helper in `ml_shadow_test_utils.py` is called by:
- `test_ml_prediction_engine.py`
- `test_ml_shadow_signal_generator.py`
- `test_ml_shadow_leaderboard.py`
- `test_ml_shadow_report.py`
- `test_ml_shadow_model.py`
- `test_walk_forward_dataset.py`
- `test_feature_store.py`
- `test_label_store.py`

---

## 5. Test Gap Analysis

### P0: Must Add

| ID | Gap | Rationale | Status |
|----|-----|-----------|--------|
| D2 | `run-daily` does not import ML shadow modules | Critical boundary — must be tested via import inspection | **Missing** |
| D4 | Feature columns do not contain `future_*` fields | Data leakage prevention | **Missing** |
| D5 | Walk-forward rows' feature columns do not contain `label_value` | Data leakage prevention | **Missing** |
| D3 | Mock model `prediction_score` does not equal `label_value` | Anti-cheat verification | **Missing** |
| D6 | Shadow signals cannot be accepted by order generator | Boundary isolation | **Missing** |
| D15 | ML outputs always have `write_main_ledger=false` | Pollution prevention, needs dedicated assertion | **Partially covered** |

### P1: Should Add

| ID | Gap | Rationale | Status |
|----|-----|-----------|--------|
| D1 | `run-daily` does not import labels module | Partially covered by `test_run_daily_does_not_read_label_files` (functional), but import-level check is missing | **Partially covered** |
| D7 | `recommendation=watch/promising` does not trigger promotion | No auto-promotion path exists, but test should verify | **Missing** |
| D10 | Report contains "not used by run-daily" | Wording verification for shadow report | **Covered** in `test_ml_shadow_report.py` |

### P2: Can Defer

| ID | Gap | Rationale | Status |
|----|-----|-----------|--------|
| D8 | Replay directory isolation from daily-run | `ReplayPaths` enforces via class design; `write_main_ledger` raises ValueError | **Implicitly covered** |
| D9 | Repeated CLI execution idempotency | Low risk given file-based architecture | **Missing** |
| D11 | Windows path compatibility | Running on Windows already; tests pass | **Low risk** |
| D12 | `source`/`quality` field missing = safe failure | Error handling exists but not explicitly tested | **Missing** |

---

## 6. Report Wording Review

| Check | File | Verdict | Notes |
|-------|------|---------|-------|
| E1: mock model ≠ real ML | `shadow_report.py:97` | ✅ PASS | "mock model is for pipeline validation only; lightgbm is optional" |
| E2: watch ≠ deployable | `shadow_leaderboard.py:154` | ✅ PASS | "shadow-only: recommendation means continue observation only" |
| E3: price-only ≠ full replay | `historical_dry_run_replay.py:312` | ✅ PASS | `warnings.append("price-only replay: no real macro_signals were available")` |
| E4: historical ≠ forward | `historical_dry_run_replay.py:339,490` | ✅ PASS | `forward_30d_dry_run_passed: False` + "This is a historical replay and must not be represented as future 30-day forward dry-run validation." |
| E5: offline labels ≠ live signals | `label_store.py:244-246` | ✅ PASS | "labels are offline-only / labels use future data by design / labels must not be used in run-daily decision path" |
| E6: shadow signals ≠ active | `shadow_signal_generator.py:97-101` | ✅ PASS | "shadow_only=true / not active / no orders generated / no trades generated" |

**No overstatements found in reports.**

---

## 7. Recommended Test Additions

### New file: `tests/test_ml_shadow_boundaries.py`

| Test Function | Covers |
|---------------|--------|
| `test_run_daily_does_not_import_labels_module` | D1 — import-level check |
| `test_run_daily_does_not_import_ml_shadow_module` | D2 — import-level check |
| `test_label_files_not_read_by_run_daily` | D1 — functional check (already exists, included for completeness) |
| `test_ml_predictions_do_not_write_main_ledger_paths` | C5+D15 — explicit path check |
| `test_shadow_signals_not_accepted_by_order_generator` | D6 — boundary isolation |
| `test_feature_columns_do_not_contain_future_fields` | D4 — data leakage |
| `test_walk_forward_feature_columns_do_not_contain_label_value` | D5 — data leakage |
| `test_mock_model_prediction_score_not_equal_to_label_value` | D3 — anti-cheat |
| `test_shadow_report_contains_not_used_by_run_daily` | D10 — wording |
| `test_ml_pipeline_outputs_write_main_ledger_is_false` | D15 — pollution flag |
| `test_shadow_recommendation_does_not_trigger_promotion` | D7 — no auto-promotion |
| `test_label_available_false_excluded_from_training` | D13 — label exclusion |

---

## 8. Final Verdict

### **PASS_WITH_TEST_GAPS**

The system architecture is sound. All boundary checks pass. No data leakage, no main ledger pollution, no report overstatements. The only gap is the absence of dedicated boundary tests in a single comprehensive test file. These tests are recommended as P0/P1 additions to harden the test suite against future regressions.
