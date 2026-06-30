from tests.a_share_build_output_ops_test_utils import AS_OF_DATE
from trading_core.equity_owner_daily_pack.daily_pack_config import (
    ALLOWED_MODES,
    BUILD_DECISION_PACK,
    DailyPackConfig,
    TARGET_VERSION,
    validate_config,
)


def test_owner_daily_pack_config_defaults():
    config = DailyPackConfig(as_of_date=AS_OF_DATE).to_dict()
    assert config["target_version"] == TARGET_VERSION
    assert config["mode"] == BUILD_DECISION_PACK
    assert config["source_workflow_mode"] == "build_from_existing_data"
    assert config["not_investment_decision_pack"] is True
    assert config["rerun_build_from_existing_data"] is False
    assert config["allow_broker"] is False
    assert config["allow_buy_sell_signals"] is False
    assert config["allowed_modes"] == ALLOWED_MODES


def test_owner_daily_pack_config_rejects_invalid_mode():
    assert validate_config(DailyPackConfig(as_of_date=AS_OF_DATE, mode="buy_stock"))
