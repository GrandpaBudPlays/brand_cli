from pathlib import Path
from typing import Optional
from brand_cli.fragments.base import Fragment

class StaticFragment(Fragment):
    """Fragment that returns exact file content"""
    
    def resolve(self) -> str:
        try:
            if self._content is None:
                self._content = self.path.read_text(encoding='utf-8')
            return self._content
        except Exception as e:
            return f"[FRAGMENT_ERROR] StaticFragment@{self.path}: {str(e)}"