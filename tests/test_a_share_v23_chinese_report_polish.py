from __future__ import annotations

from pathlib import Path

from a_share_v23_test_utils import make_v23_paths, v23_json
from trading_core.equity_v23_operator_ux_journal.builder import run_a_share_v23_operator_ux_journal


def test_v23_chinese_report_polish_scans_forbidden_wording(tmp_path: Path) -> None:
    paths = make_v23_paths(tmp_path)
    result = run_a_share_v23_operator_ux_journal(paths=paths, simulation_only=True)
    polish = v23_json(paths, "v23_chinese_report_polish_result")

    assert result["chinese_report_polish_generated"] is True
    assert polish["terminology_consistency_map"]["research-only"] == "仅研究用途"
    assert "建议买入" in polish["forbidden_phrases"]
    assert "模拟观察" in polish["allowed_phrases"]
    assert polish["report_polish_changes_underlying_result"] is False
