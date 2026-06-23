from trading_core.evolution.experiment_queue import update_experiment_queue
from trading_core.storage.file_paths import project_paths


def test_experiment_queue_deduplicates(sample_workspace) -> None:
    memory = {
        "rules": [
            {
                "rule_id": "R1",
                "strategy_id": "macro",
                "hypothesis": "test",
                "status": "proposed",
            }
        ]
    }
    paths = project_paths(sample_workspace)
    first = update_experiment_queue("2026-06-23", memory, paths=paths)
    second = update_experiment_queue("2026-06-24", memory, paths=paths)
    assert len(first) == len(second)
    assert second[0]["test_mode"] == "shadow"
