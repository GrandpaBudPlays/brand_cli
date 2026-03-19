from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

class Fragment(ABC):
    """Base abstract class for all fragment types"""
    
    def __init__(self, path: Path):
        self.path = path
        self._content: Optional[str] = None
    
    @abstractmethod
    def resolve(self) -> str:
        """Resolve fragment content"""
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.path})"