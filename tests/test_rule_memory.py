from trading_core.evolution.rule_memory import update_rule_memory
from trading_core.storage.file_paths import project_paths


def test_rule_memory_deduplicates_rules(sample_workspace) -> None:
    mistake = {
        "strategy_id": "macro",
        "mistake_type": "benchmark_underperformance",
        "signal_id": "S1",
    }
    paths = project_paths(sample_workspace)
    first = update_rule_memory("2026-06-23", [mistake], paths=paths)
    second = update_rule_memory("2026-06-24", [mistake], paths=paths)
    assert first["rules"] == []
    assert second["rules"] == []
    for index in range(3):
        second = update_rule_memory(f"2026-06-2{5 + index}", [mistake], paths=paths)
    assert len(second["rules"]) == 1
    assert len({rule["rule_id"] for rule in second["rules"]}) == len(second["rules"])
