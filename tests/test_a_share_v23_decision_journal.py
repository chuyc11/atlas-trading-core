from __future__ import annotations

from pathlib import Path

from a_share_v23_test_utils import make_v23_paths, v23_json
from trading_core.equity_v23_operator_ux_journal.builder import JOURNAL_ENTRY_TYPES, run_a_share_v23_operator_ux_journal


def test_v23_decision_journal_links_sources_and_never_generates_trade_instruction(tmp_path: Path) -> None:
    paths = make_v23_paths(tmp_path)
    result = run_a_share_v23_operator_ux_journal(paths=paths, simulation_only=True)
    journal = v23_json(paths, "v23_decision_journal_result")

    assert result["decision_journal_generated"] is True
    assert journal["allowed_journal_entry_types"] == JOURNAL_ENTRY_TYPES
    assert journal["journal_source_artifact_linkage_generated"] is True
    assert journal["journal_evidence_hash_generated"] is True
    assert journal["journal_generates_trade_instruction"] is False
    assert all(entry["journal_entry_type"] in JOURNAL_ENTRY_TYPES for entry in journal["entries"])
    assert all(entry["generates_trade_instruction"] is False for entry in journal["entries"])
