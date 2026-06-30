from trading_core.equity_owner_daily_pack_history.protected_path_trends import build_protected_path_trend_baseline


def test_protected_path_trend_clean():
    trend = build_protected_path_trend_baseline(as_of_date="2026-06-26", records=[{"protected_path_modifications_detected": False}], protected_digest={"protected_path_modifications_detected": False})
    assert trend["protected_path_trend_clean"] is True


def test_protected_path_modification_blocks_trend():
    trend = build_protected_path_trend_baseline(as_of_date="2026-06-26", records=[{"protected_path_modifications_detected": True}], protected_digest={"protected_path_modifications_detected": True})
    assert trend["protected_path_trend_clean"] is False
