from __future__ import annotations

from pathlib import Path

from a_share_feature_test_utils import AS_OF_DATE
from a_share_score_test_utils import build_score_package, make_score_paths, score_frame


def test_risk_score_range_confidence_and_breakdown_sum(tmp_path: Path) -> None:
    paths = make_score_paths(tmp_path)
    build_score_package(paths)

    base = score_frame(paths, "risk_liquidity_industry_fundamental_scores")
    breakdown = score_frame(paths, "score_component_breakdown")
    assert len(base) == 3
    assert base["RiskScore"].between(0, 100).all()
    assert base["risk_confidence"].between(0, 1).all()

    symbol = base.iloc[0]["symbol"]
    contribution_sum = breakdown[(breakdown["score_name"] == "RiskScore") & (breakdown["symbol"] == symbol)]["component_contribution"].sum()
    assert round(float(contribution_sum), 6) == float(base.loc[base["symbol"] == symbol, "RiskScore"].iloc[0])
    assert set(base["as_of_date"]) == {AS_OF_DATE}
