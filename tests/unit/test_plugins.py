"""Unit tests for PluginManifest and PluginRegistry."""

import pytest

from docforge.plugins.manifest import SUPPORTED_CAPABILITIES, PluginManifest
from docforge.plugins.registry import PluginRegistry


def _manifest(**kwargs) -> PluginManifest:
    defaults = {
        "id": "test-plugin",
        "name": "Test Plugin",
        "version": "1.0.0",
        "entrypoint": "test_plugin.plugin",
        "api_version": 1,
        "capabilities": ["image_search"],
    }
    defaults.update(kwargs)
    return PluginManifest(**defaults)


def test_manifest_has_capability():
    m = _manifest(capabilities=["image_search", "export"])
    assert m.has_capability("image_search")
    assert m.has_capability("export")
    assert not m.has_capability("ai_generate")


def test_manifest_defaults():
    m = _manifest()
    assert m.author == ""
    assert m.api_version == 1
    assert m.license == "MIT"
    assert m.requires_docforge is None
    assert m.dependencies == []


def test_registry_register_and_get():
    reg = PluginRegistry()
    m = _manifest()
    instance = object()
    reg.register(m, instance)
    assert reg.get("test-plugin") is instance


def test_registry_get_missing_returns_none():
    reg = PluginRegistry()
    assert reg.get("nope") is None


def test_registry_list_by_capability():
    reg = PluginRegistry()
    m1 = _manifest(id="p1", capabilities=["image_search"])
    m2 = _manifest(id="p2", capabilities=["export"])
    reg.register(m1, object())
    reg.register(m2, object())
    results = reg.list_by_capability("image_search")
    assert len(results) == 1
    assert results[0][0].id == "p1"


def test_registry_rejects_future_api_version():
    reg = PluginRegistry()
    m = _manifest(api_version=99)
    with pytest.raises(ValueError, match="API v99"):
        reg.register(m, object())


def test_registry_all():
    reg = PluginRegistry()
    m = _manifest()
    reg.register(m, object())
    assert "test-plugin" in reg.all


def test_supported_capabilities_is_frozenset():
    assert isinstance(SUPPORTED_CAPABILITIES, frozenset)
    assert "image_search" in SUPPORTED_CAPABILITIES
