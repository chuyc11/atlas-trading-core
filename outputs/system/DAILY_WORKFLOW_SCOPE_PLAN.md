# Daily Workflow Scope Plan

Daily workflow binding is research-only preview infrastructure and does not start forward dry-run.

## Components
- daily_market_data_snapshot
- daily_data_quality_audit
- daily_input_freeze_manifest
- daily_baseline_signal_binding
- daily_order_preview_binding
- daily_isolated_execution_preview
- daily_report_packet
- protected_path_residue_scanner
- daily_workflow_audit

## Boundary
- planning only
- run-daily not called
- forward dry-run not started
- main ledger not written
- no real-time market data download
- ML shadow not used as authorization
- LLM not used for trading decision
- RL not used
- promotion not triggered
