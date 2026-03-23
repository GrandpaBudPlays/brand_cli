import pytest
from brand_cli.prompts.base import PromptConfig, BasePrompt, PromptLibrary

class TestPromptConfig:
    def test_temperature_override(self):
        """Test model-specific temperature"""
        config = PromptConfig(
            system_instruction="test",
            user_template="test",
            temperature_overrides={"gemini": 0.5}
        )
        assert config.get_temperature("gemini") == 0.5
        assert config.get_temperature("other") == 0.1

class TestPromptLibrary:
    def test_registration(self):
        """Test prompt registration"""
        class TestPrompt(BasePrompt):
            @property
            def name(self): return "test"
            @property
            def config(self): return PromptConfig("", "")
        
        lib = PromptLibrary()
        lib.register(TestPrompt())
        assert "test" in lib.list_prompts()
        assert lib.get("test").name == "test"
        
    def test_missing_prompt(self):
        """Test error on missing prompt"""
        lib = PromptLibrary()
        with pytest.raises(KeyError):
            lib.get("missing")