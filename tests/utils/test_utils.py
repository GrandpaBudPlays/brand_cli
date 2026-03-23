from brand_cli.utils import read_file
import os
import pytest

class TestUtils:
    @pytest.mark.parametrize("content", [
        "test content",
        "",
        "multi\nline\ncontent",
    ])
    def test_read_file(self, tmp_path, content):
        """Test read_file with different content"""
        test_file = tmp_path / "test.txt"
        test_file.write_text(content)
        assert read_file(str(test_file)) == content

    def test_read_missing_file(self, tmp_path):
        """Test read_file with missing file"""
        assert read_file(str(tmp_path / "nonexistent.txt")) == ""
        
    # TODO: Add tests for file operations that require mocking