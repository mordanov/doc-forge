"""Unit tests for templates/engine.py."""
from __future__ import annotations

import pytest
import yaml

from docforge.templates import engine


@pytest.fixture(autouse=True)
def clear_theme_cache():
    engine._THEME_CACHE.clear()
    yield
    engine._THEME_CACHE.clear()


def _write_theme(directory, name, data):
    path = directory / f"{name}.yaml"
    path.write_text(yaml.dump(data))
    return path


_MINIMAL_THEME = {
    "id": "t1",
    "version": "1.0",
    "palette": {"primary": "#000"},
    "typography": {"body": "serif"},
    "spacing": {"base": 8},
}


def test_load_theme_basic(tmp_path):
    _write_theme(tmp_path, "t1", _MINIMAL_THEME)
    theme = engine.load_theme("t1", themes_dir=tmp_path)
    assert theme["id"] == "t1"
    assert theme["version"] == "1.0"


def test_load_theme_cached(tmp_path):
    _write_theme(tmp_path, "t1", _MINIMAL_THEME)
    t1 = engine.load_theme("t1", themes_dir=tmp_path)
    t2 = engine.load_theme("t1", themes_dir=tmp_path)
    assert t1 is t2  # same object from cache


def test_load_theme_not_found(tmp_path):
    with pytest.raises(FileNotFoundError, match="not found"):
        engine.load_theme("nonexistent", themes_dir=tmp_path)


def test_load_theme_missing_required_fields(tmp_path):
    _write_theme(tmp_path, "bad", {"id": "bad", "version": "1.0"})
    with pytest.raises(ValueError, match="missing required fields"):
        engine.load_theme("bad", themes_dir=tmp_path)


def test_load_theme_inheritance(tmp_path):
    parent = dict(_MINIMAL_THEME)
    parent["id"] = "parent"
    parent["palette"] = {"primary": "#fff", "secondary": "#aaa"}
    _write_theme(tmp_path, "parent", parent)

    child = {
        "id": "child",
        "version": "2.0",
        "inherits": "parent",
        "palette": {"primary": "#111"},
        "typography": {"body": "sans"},
        "spacing": {"base": 4},
    }
    _write_theme(tmp_path, "child", child)

    theme = engine.load_theme("child", themes_dir=tmp_path)
    assert theme["id"] == "child"
    assert theme["version"] == "2.0"
    # child overrides primary but inherits secondary from parent
    assert theme["palette"]["primary"] == "#111"
    assert theme["palette"]["secondary"] == "#aaa"


def test_list_themes_returns_list(tmp_path):
    _write_theme(tmp_path, "t1", _MINIMAL_THEME)
    themes = engine.list_themes(themes_dir=tmp_path)
    assert len(themes) == 1
    assert themes[0]["id"] == "t1"


def test_list_themes_skips_broken(tmp_path):
    _write_theme(tmp_path, "good", _MINIMAL_THEME)
    (tmp_path / "bad.yaml").write_text("id: bad\nversion: 1")  # missing required fields
    themes = engine.list_themes(themes_dir=tmp_path)
    assert len(themes) == 1
    assert themes[0]["id"] == "t1" or themes[0]["id"] == "good"


def test_list_themes_empty_dir(tmp_path):
    themes = engine.list_themes(themes_dir=tmp_path)
    assert themes == []


def test_deep_merge_nested():
    base = {"a": {"x": 1, "y": 2}, "b": 3}
    override = {"a": {"y": 99, "z": 100}, "c": 4}
    result = engine._deep_merge(base, override)
    assert result["a"] == {"x": 1, "y": 99, "z": 100}
    assert result["b"] == 3
    assert result["c"] == 4


def test_deep_merge_non_dict_override():
    base = {"a": {"x": 1}}
    override = {"a": "string_now"}
    result = engine._deep_merge(base, override)
    assert result["a"] == "string_now"
