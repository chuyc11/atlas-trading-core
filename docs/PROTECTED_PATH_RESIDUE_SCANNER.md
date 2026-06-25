# Protected Path Residue Scanner

The protected path residue scanner classifies local files under protected ledger-like paths. It exists to report residue, not to clean it.

## Scan Paths

- `data/orders/`
- `data/trades/`
- `data/portfolio/`
- `data/portfolios/`
- `data/accounts/`
- `outputs/orders/`
- `outputs/trades/`
- `outputs/portfolio/`
- `outputs/portfolios/`

## Classifications

- `no_residue`
- `ignored_runtime_residue`
- `tracked_protected_artifact`
- `modified_protected_artifact`
- `unknown_protected_path`

## Rules

- `ignored_runtime_residue` is a warning/nit.
- `tracked_protected_artifact` is blocking.
- `modified_protected_artifact` is blocking.
- unknown protected paths are reported explicitly.

## Forbidden Behavior

- do not delete files
- do not move files
- do not clean directories
- do not modify `.gitignore`
- do not auto-fix residue
- do not call run-daily
- do not write main ledger

