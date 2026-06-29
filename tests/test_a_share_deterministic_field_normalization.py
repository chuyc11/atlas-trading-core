import json

from trading_core.equity_build_repeatability.deterministic_normalization import normalized_json_hash


def test_deterministic_normalization_ignores_generated_at():
    a = json.dumps({"generated_at": "a", "value": 1})
    b = json.dumps({"generated_at": "b", "value": 1})
    assert normalized_json_hash(a) == normalized_json_hash(b)

