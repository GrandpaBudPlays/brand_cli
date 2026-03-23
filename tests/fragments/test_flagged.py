from brand_cli.fragments.flagged import FlaggedFragment
from pathlib import Path
import pytest

class TestFlaggedFragment:
    def test_resolve_with_tag(self, tmp_path):
        """Test resolve() with existing tag"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("[TAG:test]tag content\n")
        fragment = FlaggedFragment(test_file, "test")
        assert fragment.resolve() == "tag content"

    def test_resolve_missing_tag(self, tmp_path):
        """Test resolve() with missing tag"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("[TAG:other]content\n")
        fragment = FlaggedFragment(test_file, "test")
        result = fragment.resolve()
        assert "not found" in result

    @pytest.mark.parametrize("content,expected", [
        ("[TAG:test]content\n[TAG:test2]content2", "content"),
        ("[TAG:test]multi\nline\ncontent", "multi\nline\ncontent"),
    ])
    def test_resolve_variations(self, tmp_path, content, expected):
        """Test resolve() with different content patterns"""
        test_file = tmp_path / "test.txt"
        test_file.write_text(content)
        fragment = FlaggedFragment(test_file, "test")
        assert fragment.resolve() == expected