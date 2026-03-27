from pathlib import Path
from typing import Union, Optional
from brand_cli.fragments.base import Fragment

class StaticFragment(Fragment):
    """Fragment that returns exact file content"""
    
    def __init__(self, content_or_path: Union[str, Path]):
        self._source = content_or_path
        self._content: Optional[str] = None
        if isinstance(content_or_path, Path) or (isinstance(content_or_path, str) and Path(content_or_path).exists()):
            super().__init__(path=Path(content_or_path))
        else:
            super().__init__()
            
    def resolve(self) -> str:
        if self._content is not None:
            return self._content
            
        if isinstance(self._source, Path) or (isinstance(self._source, str) and Path(self._source).exists()):
            try:
                self._content = Path(self._source).read_text(encoding='utf-8')
            except FileNotFoundError:
                self._content = f"[FRAGMENT_ERROR] StaticFragment@{self._source}: File not found"
        else:
            self._content = str(self._source)
            
        return self._content