"""Unit tests for config loader: precedence, validation, profile merging."""

import pytest
import yaml

from docforge.config.loader import _deep_merge, load_config
from docforge.config.schema import DocForgeConfig


def test_defaults_loaded():
    cfg = load_config()
    assert cfg.project.language == "en"
    assert cfg.project.template == "minimal"
    assert cfg.ai.model == "gpt-4o"
    assert cfg.ai.creativity == 5
    assert cfg.images.enabled is True


def test_yaml_file_overrides_defaults(tmp_path):
    config_file = tmp_path / "docforge.yaml"
    config_file.write_text(
        yaml.dump({"project": {"language": "fr", "template": "corporate"}, "ai": {"creativity": 8}})
    )
    cfg = load_config(config_file=config_file)
    assert cfg.project.language == "fr"
    assert cfg.project.template == "corporate"
    assert cfg.ai.creativity == 8
    # Unspecified fields stay as defaults
    assert cfg.ai.model == "gpt-4o"


def test_env_var_overrides_defaults(monkeypatch):
    monkeypatch.setenv("DOCFORGE_PROJECT_LANGUAGE", "ru")
    cfg = load_config()
    assert cfg.project.language == "ru"


def test_creativity_validation_range():
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        DocForgeConfig(ai={"creativity": 0})  # below min
    with pytest.raises(ValidationError):
        DocForgeConfig(ai={"creativity": 11})  # above max


def test_server_port_validation():
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        DocForgeConfig(server={"port": 0})
    with pytest.raises(ValidationError):
        DocForgeConfig(server={"port": 99999})


def test_deep_merge_overrides_leaf():
    base = {"a": {"x": 1, "y": 2}, "b": 3}
    override = {"a": {"y": 99}, "c": 4}
    result = _deep_merge(base, override)
    assert result == {"a": {"x": 1, "y": 99}, "b": 3, "c": 4}


def test_deep_merge_non_dict_override():
    base = {"a": {"x": 1}}
    override = {"a": "scalar"}
    result = _deep_merge(base, override)
    assert result["a"] == "scalar"


def test_load_config_returns_docforgeconfig_type():
    cfg = load_config()
    assert isinstance(cfg, DocForgeConfig)


def test_images_policy_invalid(monkeypatch):
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        DocForgeConfig(images={"policy": "nonexistent_policy"})
