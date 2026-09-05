from __future__ import annotations

import pytest

import trading_core.cli as cli

pytestmark = pytest.mark.smoke


@pytest.mark.parametrize(
    "command",
    [
        "generate-signals",
        "generate-orders",
        "execute",
        "mark",
        "benchmark",
        "attribution",
        "score-signals",
        "classify-mistakes",
        "score-strategies",
        "update-rule-memory",
        "update-experiment-queue",
        "run-evolution",
        "report",
    ],
)
def test_unimplemented_stage_commands_fail_closed(command, monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli, "run_daily", lambda *_args, **_kwargs: pytest.fail("run_daily must not be called"))

    assert cli.main([command, "--date", "2026-07-10"]) == 2
    assert "not implemented as an isolated stage" in capsys.readouterr().err
