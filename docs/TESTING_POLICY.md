# Testing Policy

## v0.8.17 Targeted Test Policy

For `v0.8.17-a-share-owner-readiness-controlled-gate-reevaluation`, the required validation is targeted pytest only:

```bash
python -m pytest tests/test_a_share_owner_readiness_controlled_gate_reevaluation*.py tests/test_a_share_controlled_gate_reevaluation*.py
```

On Windows PowerShell, expand the same targeted file set before invoking pytest:

```powershell
$tests = @(Get-ChildItem tests -Filter 'test_a_share_owner_readiness_controlled_gate_reevaluation*.py') + @(Get-ChildItem tests -Filter 'test_a_share_controlled_gate_reevaluation*.py')
python -m pytest @($tests.FullName)
```

The v0.8.17 release report must include:

- `full_pytest_run=false`
- `targeted_pytest_passed=true`
- `targeted_pytest_count=<actual>`
- `full_pytest_deferred_until=v0.9.0 or next big-version closeout`

Full pytest is deferred until `v0.9.0` or the next big-version closeout unless explicitly requested.

