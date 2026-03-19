from pathlib import Path
import re
from .base import Fragment
from typing import Dict

class FlaggedFragment(Fragment):
    """Fragment that retrieves tagged sections from file"""
    
    TAG_PATTERN = re.compile(r'\[TAG:(.*?)\]([\s\S]*?)(?=\n\[TAG:|$)')
    
    def __init__(self, path: Path, tag: str):
        super().__init__(path)
        self.tag = tag
        self._tags: Dict[str, str] = {}
    
    def resolve(self) -> str:
        try:
            if not self._tags:
                content = self.path.read_text(encoding='utf-8')
                self._tags = dict(self.TAG_PATTERN.findall(content))
            return self._tags.get(self.tag, 
                f"[FRAGMENT_ERROR] FlaggedFragment@{self.path}: Tag '{self.tag}' not found")
        except Exception as e:
            return f"[FRAGMENT_ERROR] FlaggedFragment@{self.path}: {str(e)}"