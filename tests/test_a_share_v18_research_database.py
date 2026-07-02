from __future__ import annotations

from pathlib import Path

from a_share_v18_test_utils import make_v18_paths, v18_json
from trading_core.equity_v18_research_db_feature_ml_lab.builder import run_a_share_v18_research_db_feature_ml_lab


def test_v18_research_database_registry_and_snapshot_reproducibility(tmp_path: Path) -> None:
    paths = make_v18_paths(tmp_path)
    result = run_a_share_v18_research_db_feature_ml_lab(paths=paths, simulation_only=True)
    registry = v18_json(paths, "v18_research_database_registry")
    snapshot = v18_json(paths, "v18_storage_snapshot_reproducibility_result")

    assert result["research_database_registry_generated"] is True
    assert registry["research_table_registry_generated"] is True
    assert registry["symbol_date_primary_key_check"] == "passed_by_contract"
    assert registry["as_of_date_index_check"] == "passed"
    assert registry["local_file_backed_storage_supported"] is True
    assert snapshot["storage_snapshot_reproducibility_result_generated"] is True
    assert snapshot["snapshot_reproducibility_check"] == "passed"
    assert snapshot["snapshot_lineage_fabricated"] is False
