from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class ModelResult:
    model_name: str
    content: str
    success: bool
    error: Optional[str] = None
    input_tokens: int = 0
    output_tokens: int = 0
    cost: float = 0.0
    fallback_used: bool = False


class BaseAIModel(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def generate(self, prompt: str, system_instruction: str = "", temperature: float = 0.1, response_mime_type: str = "text/plain", response_schema: dict | None = None, file_obj: Optional[Any] = None) -> ModelResult:
        pass
