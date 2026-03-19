from pathlib import Path
import random
from brand_cli.fragments.base import Fragment

class RandomFragment(Fragment):
    """Fragment that returns a random block from delimited file"""
    
    def __init__(self, path: Path, delimiter: str = "\n---\n"):
        super().__init__(path)
        self.delimiter = delimiter
    
    def resolve(self) -> str:
        try:
            if self._content is None:
                self._content = self.path.read_text(encoding='utf-8')
            blocks = self._content.split(self.delimiter)
            return random.choice(blocks).strip()
        except Exception as e:
            return f"[FRAGMENT_ERROR] RandomFragment@{self.path}: {str(e)}"