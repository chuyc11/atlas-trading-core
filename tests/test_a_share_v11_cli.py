from __future__ import annotations

from pathlib import Path

import pytest

from a_share_v11_test_utils import make_v11_paths


def test_v11_cli_run_audit_build_commands_and_owner_status_still_works(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_v11_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "owner_daily_status_output", lambda **_: '{"known_owner_readiness_state":"blocked"}')

    assert cli.main(["run-a-share-v11-owner-ops-platform", "--as-of-date", "2026-07-01", "--simulation-only", "--dry-run"]) == 0
    assert cli.main(["run-a-share-v11-owner-ops-platform", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-owner-command-center", "--as-of-date", "2026-07-01"]) == 0
    assert cli.main(["build-a-share-simulated-account-reconciliation", "--as-of-date", "2026-07-01"]) == 0
    assert cli.main(["build-a-share-strategy-lifecycle-review", "--as-of-date", "2026-07-01"]) == 0
    assert cli.main(["build-a-share-monitoring-remediation-pack", "--as-of-date", "2026-07-01"]) == 0
    assert cli.main(["audit-a-share-v11-owner-ops-platform", "--as-of-date", "2026-07-01"]) == 0
    assert cli.main(["run-and-audit-a-share-v11-owner-ops-platform", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["owner-daily-status", "--as-of-date", "2026-07-01", "--format", "json"]) == 0


def test_v11_cli_requires_simulation_only_flag(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_v11_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)

    assert cli.main(["run-a-share-v11-owner-ops-platform", "--as-of-date", "2026-07-01"]) == 1
