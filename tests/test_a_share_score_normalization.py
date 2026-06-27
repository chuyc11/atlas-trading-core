from __future__ import annotations

import math

import pandas as pd

from trading_core.equity_scoring.normalization import component_score, percentile_score, winsorize_series


def test_score_normalization_winsor_percentile_and_missing_confidence() -> None:
    clipped = winsorize_series(pd.Series([1.0, 2.0, 3.0, 1000.0]), lower=0.25, upper=0.75)
    assert clipped.max() < 1000.0

    higher = percentile_score(pd.Series([1.0, 2.0, 3.0]), direction="higher")
    lower = percentile_score(pd.Series([1.0, 2.0, 3.0]), direction="lower")
    assert higher.iloc[-1] == 100.0
    assert lower.iloc[0] == 100.0

    boolean = percentile_score(pd.Series([True, False, math.nan]), direction="boolean_higher")
    assert boolean.iloc[2] == 50.0

    frame = pd.DataFrame({"present": [1.0, None, 3.0]})
    score, confidence, coverage = component_score(frame, ["present", "missing"], {"present": "higher"})
    assert score.between(0, 100).all()
    assert confidence.tolist() == [0.5, 0.0, 0.5]
    assert coverage["present"] == round(2 / 3, 6)
    assert coverage["missing"] == 0.0
