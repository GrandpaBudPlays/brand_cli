from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
from pathlib import Path
from brand_cli.prompts.loader import PromptLoader


@dataclass
class PromptConfig:
    system_instruction: str
    user_template: str
    temperature: float = 0.1
    temperature_overrides: dict[str, float] = field(default_factory=dict)
    
    def get_temperature(self, model_name: str) -> float:
        return self.temperature_overrides.get(model_name, self.temperature)


class BasePrompt(ABC):
    def __init__(self, prompts_dir: str = "resources/prompts"):
        self._loader = PromptLoader(prompts_dir)
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this prompt"""
        pass
    
    @property
    @abstractmethod
    def config(self) -> PromptConfig:
        """Return the prompt configuration"""
        pass
    
    def build_prompt(self, **kwargs: Any) -> str:
        """Build the user prompt from template with provided variables"""
        try:
            loaded = self._loader.load_prompt(
                operation_name=self.name,
                fragments=kwargs.get("fragments", {}),
                session_data=kwargs.get("session_data", {})
            )
            return loaded["user_prompt"]
        except ValueError:
            # Fall back to original format if YAML not found
            return self.config.user_template.format(**kwargs)
    
    def get_system_instruction(self) -> str:
        """Return the system instruction"""
        try:
            loaded = self._loader.load_prompt(
                operation_name=self.name,
                fragments={},
                session_data={}
            )
            return loaded["system_prompt"]
        except ValueError:
            # Fall back to original if YAML not found
            return self.config.system_instruction
    
    def get_temperature(self, model_name: str) -> float:
        """Get model-specific temperature"""
        return self.config.get_temperature(model_name)


class PromptLibrary:
    """Registry of all available prompts"""
    
    def __init__(self):
        self._prompts: dict[str, BasePrompt] = {}
    
    def register(self, prompt: BasePrompt):
        self._prompts[prompt.name] = prompt
    
    def get(self, name: str) -> BasePrompt:
        if name not in self._prompts:
            raise KeyError(f"Prompt '{name}' not found. Available: {list(self._prompts.keys())}")
        return self._prompts[name]
    
    def list_prompts(self) -> list[str]:
        return list(self._prompts.keys())
