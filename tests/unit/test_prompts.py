"""Unit tests for prompt loader."""

import pytest

from docforge.ai.prompts.loader import _load_file, list_prompts, load_prompt


def test_load_prompt_not_found_raises():
    with pytest.raises(FileNotFoundError, match="nonexistent-prompt"):
        load_prompt("nonexistent-prompt")


def test_list_prompts_from_missing_dir(tmp_path):
    missing = tmp_path / "no-such-dir"
    result = list_prompts(prompts_dir=missing)
    assert result == []


def test_load_file_from_yaml(tmp_path):
    yaml_content = """
id: test-prompt
version: "1.0"
description: A test prompt
providers:
  - openai
template: "Summarise: {{ text }}"
response_schema: {}
context_fields:
  - text
"""
    p = tmp_path / "test-prompt.yaml"
    p.write_text(yaml_content)
    prompt = _load_file(p)
    assert prompt.id == "test-prompt"
    assert prompt.version == "1.0"
    assert "Summarise" in prompt.template
    assert "openai" in prompt.providers


def test_list_prompts_returns_loaded(tmp_path):
    yaml_content = """
id: list-test
version: "1.0"
description: List test
providers: []
template: "Hello"
response_schema: {}
"""
    (tmp_path / "list-test.yaml").write_text(yaml_content)
    result = list_prompts(prompts_dir=tmp_path)
    assert len(result) == 1
    assert result[0].id == "list-test"


def test_list_prompts_skips_bad_yaml(tmp_path):
    (tmp_path / "bad.yaml").write_text(": invalid: yaml: [")
    result = list_prompts(prompts_dir=tmp_path)
    assert result == []
