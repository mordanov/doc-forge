"""Unit tests for config/loader.py."""
from __future__ import annotations

import pytest
import yaml

from docforge.config.loader import _deep_merge, _find_profile, _load_file, load_config


def test_load_file_yaml(tmp_path):
    f = tmp_path / "cfg.yaml"
    f.write_text("ai:\n  model: gpt-4o\n")
    result = _load_file(f)
    assert result["ai"]["model"] == "gpt-4o"


def test_load_file_yml(tmp_path):
    f = tmp_path / "cfg.yml"
    f.write_text("templates:\n  default: minimal\n")
    result = _load_file(f)
    assert result["templates"]["default"] == "minimal"


def test_load_file_toml(tmp_path):
    f = tmp_path / "cfg.toml"
    f.write_bytes(b'[ai]\nmodel = "gpt-4o"\n')
    result = _load_file(f)
    assert result["ai"]["model"] == "gpt-4o"


def test_load_file_unsupported_format(tmp_path):
    f = tmp_path / "cfg.json"
    f.write_text("{}")
    with pytest.raises(ValueError, match="Unsupported config file format"):
        _load_file(f)


def test_load_file_empty_yaml(tmp_path):
    f = tmp_path / "empty.yaml"
    f.write_text("")
    result = _load_file(f)
    assert result == {}


def test_deep_merge_overrides():
    base = {"a": 1, "b": {"x": 10, "y": 20}}
    override = {"b": {"y": 99}, "c": 3}
    result = _deep_merge(base, override)
    assert result == {"a": 1, "b": {"x": 10, "y": 99}, "c": 3}


def test_deep_merge_non_dict_wins():
    base = {"a": {"nested": 1}}
    override = {"a": "flat"}
    result = _deep_merge(base, override)
    assert result["a"] == "flat"


def test_find_profile_returns_none_for_missing():
    result = _find_profile("nonexistent_profile_xyz")
    assert result is None


def test_load_config_returns_config():
    # Basic smoke test — loads defaults without a file
    config = load_config()
    assert config is not None


def test_load_config_with_yaml_file(tmp_path):
    f = tmp_path / "custom.yaml"
    f.write_text("")  # empty but valid
    config = load_config(config_file=f)
    assert config is not None


def test_load_config_unknown_profile(tmp_path):
    # Unknown profile is silently ignored
    config = load_config(profile="nonexistent_xyz")
    assert config is not None
