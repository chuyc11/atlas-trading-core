from trading_core.config_loader import load_all_configs, load_config


def test_config_files_load() -> None:
    configs = load_all_configs()
    assert configs["settings.yaml"]["run_mode"]["allow_real_trading"] is False
    assert load_config("universe_china_etf.yaml")["universe_id"] == "china_etf_core_v1"
