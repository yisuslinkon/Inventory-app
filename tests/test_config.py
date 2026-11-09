from inventory_app import config


def test_data_dir_override(monkeypatch, tmp_path):
    target = tmp_path / "otra"
    monkeypatch.setenv(config.ENV_DATA_DIR, str(target))
    assert config.is_custom_data_dir()
    assert config.data_dir() == target.resolve()
    assert target.is_dir()
    assert config.db_path() == target.resolve() / config.DB_FILENAME


def test_no_override_flag(monkeypatch):
    monkeypatch.delenv(config.ENV_DATA_DIR, raising=False)
    assert not config.is_custom_data_dir()
