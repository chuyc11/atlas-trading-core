from trading_core import config_loader
from trading_core.config_loader import load_all_configs, load_config


def test_config_files_load() -> None:
    configs = load_all_configs()
    assert configs["settings.yaml"]["run_mode"]["allow_real_trading"] is False
    assert load_config("universe_china_etf.yaml")["universe_id"] == "china_etf_core_v1"


def test_packaged_config_defaults_load_without_source_config(monkeypatch) -> None:
    monkeypatch.setattr(config_loader, "CONFIG_DIR", config_loader.PACKAGE_CONFIG_DIR)

    configs = config_loader.load_all_configs()

    assert configs["settings.yaml"]["run_mode"]["allow_real_trading"] is False
    assert configs["risk_rules.yaml"]["limits"]["min_cash_weight"] == 0.10
