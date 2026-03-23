from brand_cli.fragments.static import StaticFragment
from pathlib import Path
import pytest

class TestStaticFragment:
    def test_resolve_with_content(self, tmp_path):
        """Test resolve() when content is already loaded"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        fragment = StaticFragment(test_file)
        fragment._content = "preloaded content"
        assert fragment.resolve() == "preloaded content"

    def test_resolve_with_file(self, tmp_path):
        """Test resolve() when reading from file"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("file content")
        fragment = StaticFragment(test_file)
        assert fragment.resolve() == "file content"

    def test_resolve_error(self, tmp_path):
        """Test resolve() when file doesn't exist"""
        fragment = StaticFragment(tmp_path / "nonexistent.txt")
        result = fragment.resolve()
        assert "[FRAGMENT_ERROR]" in result