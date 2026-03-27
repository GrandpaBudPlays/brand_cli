from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

class Fragment(ABC):
    def __init__(self, path: Optional[Path] = None, raw_content: Optional[str] = None):
        self.path = path
        self.raw_content = raw_content

    @abstractmethod
    def resolve(self) -> str:
        """Return the processed string content of the fragment."""
        pass

    def __repr__(self) -> str:
        # Show path if it exists, otherwise show a snippet of the raw content
        identifier = self.path if self.path else f"raw:{str(self.raw_content)[:20]}..."
        return f"{self.__class__.__name__}({identifier})"