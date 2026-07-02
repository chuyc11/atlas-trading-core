from __future__ import annotations

from pathlib import Path

import pytest

from a_share_v15_test_utils import make_v15_paths


def test_v15_cli_build_audit_specialty_commands_and_owner_status(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_v15_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "owner_daily_status_output", lambda **_: '{"known_owner_readiness_state":"blocked"}')

    assert cli.main(["build-a-share-v15-market-regime-lab", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-market-regime-classification", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-regime-factor-candidate-review", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-regime-strategy-review", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-adaptive-research-queue", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-regime-llm-rl-governance", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-regime-portfolio-overlay", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["audit-a-share-v15-market-regime-lab", "--as-of-date", "2026-07-01"]) == 0
    assert cli.main(["build-and-audit-a-share-v15-market-regime-lab", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["owner-daily-status", "--as-of-date", "2026-07-01", "--format", "json"]) == 0


def test_v15_cli_requires_simulation_only_flag(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_v15_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)

    assert cli.main(["build-a-share-v15-market-regime-lab", "--as-of-date", "2026-07-01"]) == 1
    assert cli.main(["build-a-share-regime-portfolio-overlay", "--as-of-date", "2026-07-01"]) == 1
