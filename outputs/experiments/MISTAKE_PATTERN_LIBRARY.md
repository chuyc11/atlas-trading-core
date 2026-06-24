# Mistake Pattern Library

## 1. Scope

* library_id: MISTAKE-LIB-20260624-001
* created_at: 2026-06-24T16:01:40.505393Z
* input count: 4
* pattern count: 4
* min_evidence: 2

## 2. Summary

| pattern_type | evidence_count | severity | affected_strategies | affected_experiments | affected_models | suggested_action | status |
|---|---:|---|---|---|---|---|---|
| unstable_rank_ic | 242 | high |  |  | MLSHADOW-20240101-20260623-mock | keep_shadow | monitoring |
| benchmark_underperformance | 48 | high | momentum_strategy_v1 | EXP-sweep-momentum-20260624 |  | compare_benchmark | open |
| cost_drag | 24 | high | momentum_strategy_v1 | EXP-sweep-momentum-20260624 |  | reduce_turnover | open |
| overfit_parameter | 24 | high | momentum_strategy_v1 | EXP-sweep-momentum-20260624 |  | require_more_data | open |

## 3. Patterns

### PATTERN-0001 - unstable_rank_ic

* description: ML shadow rank IC appears weak or unstable.
* severity: high
* evidence_count: 242
* affected_strategies: none
* affected_experiments: none
* affected_models: MLSHADOW-20240101-20260623-mock
* suggested_action: keep_shadow
* status: monitoring

Evidence examples

| source_type | source_id | item_id | metric | value | reason |
|---|---|---|---|---:|---|
| ml_shadow_leaderboard | MLSHADOW-20240101-20260623-mock | WF-0001:2025-04-01 | rank_ic | -0.0952381 | rank IC instability |
| ml_shadow_leaderboard | MLSHADOW-20240101-20260623-mock | WF-0001:2025-04-02 | rank_ic | 0.190476 | rank IC instability |
| ml_shadow_leaderboard | MLSHADOW-20240101-20260623-mock | WF-0001:2025-04-03 | rank_ic | 0.0238095 | rank IC instability |
| ml_shadow_leaderboard | MLSHADOW-20240101-20260623-mock | WF-0001:2025-04-07 | rank_ic | -0.619048 | rank IC instability |
| ml_shadow_leaderboard | MLSHADOW-20240101-20260623-mock | WF-0001:2025-04-08 | rank_ic | -0.738095 | rank IC instability |
| ml_shadow_leaderboard | MLSHADOW-20240101-20260623-mock | WF-0001:2025-04-09 | rank_ic | -0.428571 | rank IC instability |
| ml_shadow_leaderboard | MLSHADOW-20240101-20260623-mock | WF-0001:2025-04-10 | rank_ic | -0.238095 | rank IC instability |
| ml_shadow_leaderboard | MLSHADOW-20240101-20260623-mock | WF-0001:2025-04-11 | rank_ic | -0.47619 | rank IC instability |
| ml_shadow_leaderboard | MLSHADOW-20240101-20260623-mock | WF-0001:2025-04-14 | rank_ic | -0.547619 | rank IC instability |
| ml_shadow_leaderboard | MLSHADOW-20240101-20260623-mock | WF-0001:2025-04-15 | rank_ic | 0.5 | rank IC instability |
| ml_shadow_leaderboard | MLSHADOW-20240101-20260623-mock | WF-0001:2025-04-16 | rank_ic | -0.809524 | rank IC instability |
| ml_shadow_leaderboard | MLSHADOW-20240101-20260623-mock | WF-0001:2025-04-17 | rank_ic | -0.904762 | rank IC instability |
| ml_shadow_leaderboard | MLSHADOW-20240101-20260623-mock | WF-0001:2025-04-18 | rank_ic | -0.771429 | rank IC instability |
| ml_shadow_leaderboard | MLSHADOW-20240101-20260623-mock | WF-0001:2025-04-21 | rank_ic | -0.314286 | rank IC instability |
| ml_shadow_leaderboard | MLSHADOW-20240101-20260623-mock | WF-0001:2025-04-22 | rank_ic | -0.761905 | rank IC instability |
| ml_shadow_leaderboard | MLSHADOW-20240101-20260623-mock | WF-0001:2025-04-23 | rank_ic | -0.166667 | rank IC instability |
| ml_shadow_leaderboard | MLSHADOW-20240101-20260623-mock | WF-0001:2025-04-24 | rank_ic | -0.333333 | rank IC instability |
| ml_shadow_leaderboard | MLSHADOW-20240101-20260623-mock | WF-0001:2025-04-25 | rank_ic | -0.214286 | rank IC instability |
| ml_shadow_leaderboard | MLSHADOW-20240101-20260623-mock | WF-0001:2025-04-28 | rank_ic | -0.571429 | rank IC instability |
| ml_shadow_leaderboard | MLSHADOW-20240101-20260623-mock | WF-0001:2025-04-29 | rank_ic | -0.690476 | rank IC instability |

### PATTERN-0002 - benchmark_underperformance

* description: Candidates underperformed their benchmark or EQUAL_ETF reference.
* severity: high
* evidence_count: 48
* affected_strategies: momentum_strategy_v1
* affected_experiments: EXP-sweep-momentum-20260624
* affected_models: none
* suggested_action: compare_benchmark
* status: open

Evidence examples

| source_type | source_id | item_id | metric | value | reason |
|---|---|---|---|---:|---|
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-001 | excess_return_vs_equal_etf | -0.908018 | negative excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-002 | excess_return_vs_equal_etf | -0.897057 | negative excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-003 | excess_return_vs_equal_etf | -0.867825 | negative excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-004 | excess_return_vs_equal_etf | -0.883543 | negative excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-005 | excess_return_vs_equal_etf | -0.850191 | negative excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-006 | excess_return_vs_equal_etf | -0.791905 | negative excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-007 | excess_return_vs_equal_etf | -0.913841 | negative excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-008 | excess_return_vs_equal_etf | -0.905514 | negative excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-009 | excess_return_vs_equal_etf | -0.899678 | negative excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-010 | excess_return_vs_equal_etf | -0.886768 | negative excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-011 | excess_return_vs_equal_etf | -0.860037 | negative excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-012 | excess_return_vs_equal_etf | -0.837834 | negative excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-013 | excess_return_vs_equal_etf | -1.01475 | negative excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-014 | excess_return_vs_equal_etf | -1.01061 | negative excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-015 | excess_return_vs_equal_etf | -0.98315 | negative excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-016 | excess_return_vs_equal_etf | -0.993179 | negative excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-017 | excess_return_vs_equal_etf | -0.973118 | negative excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-018 | excess_return_vs_equal_etf | -0.920767 | negative excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-019 | excess_return_vs_equal_etf | -0.91354 | negative excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-020 | excess_return_vs_equal_etf | -0.896001 | negative excess return |

### PATTERN-0003 - cost_drag

* description: Costs appear to drag performance while excess return is non-positive.
* severity: high
* evidence_count: 24
* affected_strategies: momentum_strategy_v1
* affected_experiments: EXP-sweep-momentum-20260624
* affected_models: none
* suggested_action: reduce_turnover
* status: open

Evidence examples

| source_type | source_id | item_id | metric | value | reason |
|---|---|---|---|---:|---|
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-001 | cost_ratio | 0.024914 | cost drag with non-positive excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-002 | cost_ratio | 0.046659 | cost drag with non-positive excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-003 | cost_ratio | 0.056757 | cost drag with non-positive excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-004 | cost_ratio | 0.025878 | cost drag with non-positive excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-005 | cost_ratio | 0.048516 | cost drag with non-positive excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-006 | cost_ratio | 0.059075 | cost drag with non-positive excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-007 | cost_ratio | 0.025974 | cost drag with non-positive excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-008 | cost_ratio | 0.044515 | cost drag with non-positive excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-009 | cost_ratio | 0.062002 | cost drag with non-positive excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-010 | cost_ratio | 0.02698 | cost drag with non-positive excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-011 | cost_ratio | 0.046244 | cost drag with non-positive excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-012 | cost_ratio | 0.06444 | cost drag with non-positive excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-013 | cost_ratio | 0.028088 | cost drag with non-positive excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-014 | cost_ratio | 0.047712 | cost drag with non-positive excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-015 | cost_ratio | 0.054616 | cost drag with non-positive excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-016 | cost_ratio | 0.029166 | cost drag with non-positive excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-017 | cost_ratio | 0.049599 | cost drag with non-positive excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-018 | cost_ratio | 0.056809 | cost drag with non-positive excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-019 | cost_ratio | 0.016436 | cost drag with non-positive excess return |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-020 | cost_ratio | 0.0244 | cost drag with non-positive excess return |

### PATTERN-0004 - overfit_parameter

* description: Parameter scores vary widely without a durable candidate signal.
* severity: high
* evidence_count: 24
* affected_strategies: momentum_strategy_v1
* affected_experiments: EXP-sweep-momentum-20260624
* affected_models: none
* suggested_action: require_more_data
* status: open

Evidence examples

| source_type | source_id | item_id | metric | value | reason |
|---|---|---|---|---:|---|
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-001 | score | -91.91 | score dispersion is high and no best shadow candidate was selected |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-002 | score | -91.89 | score dispersion is high and no best shadow candidate was selected |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-003 | score | -89.29 | score dispersion is high and no best shadow candidate was selected |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-004 | score | -89.98 | score dispersion is high and no best shadow candidate was selected |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-005 | score | -88.07 | score dispersion is high and no best shadow candidate was selected |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-006 | score | -82.69 | score dispersion is high and no best shadow candidate was selected |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-007 | score | -92.48 | score dispersion is high and no best shadow candidate was selected |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-008 | score | -92.75 | score dispersion is high and no best shadow candidate was selected |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-009 | score | -92.64 | score dispersion is high and no best shadow candidate was selected |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-010 | score | -90.14 | score dispersion is high and no best shadow candidate was selected |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-011 | score | -88.98 | score dispersion is high and no best shadow candidate was selected |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-012 | score | -87.51 | score dispersion is high and no best shadow candidate was selected |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-013 | score | -102.57 | score dispersion is high and no best shadow candidate was selected |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-014 | score | -103.09 | score dispersion is high and no best shadow candidate was selected |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-015 | score | -100.67 | score dispersion is high and no best shadow candidate was selected |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-016 | score | -100.86 | score dispersion is high and no best shadow candidate was selected |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-017 | score | -100.06 | score dispersion is high and no best shadow candidate was selected |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-018 | score | -95.26 | score dispersion is high and no best shadow candidate was selected |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-019 | score | -92.24 | score dispersion is high and no best shadow candidate was selected |
| parameter_sweep | EXP-sweep-momentum-20260624 | EXP-sweep-momentum-20260624-RUN-020 | score | -91 | score dispersion is high and no best shadow candidate was selected |

## 4. Warnings

* insufficient evidence for pattern_type=low_sample_size: 1 < 2

## 5. Diagnostic Boundary

* This pattern library is diagnostic only.
* No strategy was modified.
* No parameter was modified.
* No promotion was triggered.
* No orders were written.
* No trades were written.
* No portfolio was written.
* No accounts were written.
* This is not an admission gate.
* This report is offline research only.
