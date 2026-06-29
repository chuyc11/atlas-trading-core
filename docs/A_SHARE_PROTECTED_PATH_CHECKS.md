# A-Share Protected Path Checks

v0.8.8 snapshots these protected paths before and after the repeat build:

- `data/orders/`
- `data/trades/`
- `data/accounts/`
- `outputs/orders/`
- `outputs/trades/`
- `outputs/accounts/`

Existing `data/orders` or `data/trades` directories are not automatically blocking. The repeatability audit distinguishes pre-existing protected paths from new, modified, or deleted protected files.

Blocking conditions:

- new protected path created by this stage
- protected file created by this stage
- protected file modified by this stage
- protected file deleted by this stage

This check exists because repeatability is research-only and virtual-only. It must not contaminate order, trade, or account paths.
