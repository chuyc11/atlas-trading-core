from __future__ import annotations

from pathlib import Path

import pytest

from a_share_v13_test_utils import make_v13_paths


def test_v13_cli_build_audit_specialty_commands_and_owner_status(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_v13_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "owner_daily_status_output", lambda **_: '{"known_owner_readiness_state":"blocked"}')

    assert cli.main(["build-a-share-v13-research-quality-lab", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-research-quality-scorecard", "--as-of-date", "2026-07-01"]) == 0
    assert cli.main(["build-a-share-strategy-lab-quality-review", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-llm-proposal-quality-review", "--as-of-date", "2026-07-01"]) == 0
    assert cli.main(["build-a-share-rl-policy-quality-review", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-strategy-lifecycle-quality-gates", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-robustness-and-overfit-review", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["audit-a-share-v13-research-quality-lab", "--as-of-date", "2026-07-01"]) == 0
    assert cli.main(["build-and-audit-a-share-v13-research-quality-lab", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["owner-daily-status", "--as-of-date", "2026-07-01", "--format", "json"]) == 0


def test_v13_cli_requires_simulation_only_flag(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_v13_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)

    assert cli.main(["build-a-share-v13-research-quality-lab", "--as-of-date", "2026-07-01"]) == 1
