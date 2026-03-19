from pathlib import Path
from typing import List
from brand_cli.fragments.base import Fragment

class CompositeFragment(Fragment):
    """Fragment that chains multiple fragments recursively"""
    
    MAX_RECURSION = 10
    
    def __init__(self, path: Path, fragments: List[Fragment]):
        super().__init__(path)
        self.fragments = fragments
        self._seen_paths = set()
    
    def resolve(self, depth: int = 0) -> str:
        if depth > self.MAX_RECURSION:
            return "[FRAGMENT_ERROR] CompositeFragment: Max recursion depth exceeded"
            
        if str(self.path) in self._seen_paths:
            return "[FRAGMENT_ERROR] CompositeFragment: Circular reference detected"
            
        self._seen_paths.add(str(self.path))
        
        try:
            results = []
            for fragment in self.fragments:
                if isinstance(fragment, CompositeFragment):
                    results.append(fragment.resolve(depth + 1))
                else:
                    results.append(fragment.resolve())
            return "\n".join(results)
        except Exception as e:
            return f"[FRAGMENT_ERROR] CompositeFragment@{self.path}: {str(e)}"