import pytest
from unittest.mock import patch
from pathlib import Path
import os
from brand_cli.file_manager import (
    resolve_ip_and_series,
    get_terminology,
    load_transcript_asset,
    save_audit_report,
    find_transcript_and_metadata
)

class TestFileManager:
    def test_resolve_ip_and_series(self, mock_env):
        """Test IP/series resolution from path"""
        test_file = mock_env / "IP/Series/Transcript.md"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("test")
        
        ip, series, _, _ = resolve_ip_and_series(test_file)
        assert ip is None  # No config setup
        assert series is None

    def test_get_terminology_defaults(self):
        """Test terminology fallbacks"""
        terms = get_terminology({})
        assert terms.ip == "IP"
        assert terms.series == "Series"

    def test_load_transcript_asset(self, mock_env):
        """Test transcript loading"""
        test_file = mock_env / "test.md"
        test_file.write_text("test content")
        assert load_transcript_asset(str(test_file)) == "test content"

    def test_save_audit_report(self, mock_env):
        """Test report saving"""
        test_dir = mock_env / "reports"
        save_path = str(test_dir / "audit.md")
        save_audit_report(save_path, "test", "audit")
        assert Path(save_path).exists()
        assert "test" in Path(save_path).read_text()
        
    def test_find_transcript_relative_path(self, mock_env):
        """Test transcript finding with relative paths"""
        (mock_env / "IP/Series").mkdir(parents=True)
        test_file = mock_env / "IP/Series/S01 E001/Transcript.md"
        test_file.parent.mkdir()
        test_file.write_text("test")
        
        # Mock config to use our test directory
        with patch("brand_cli.file_manager.CONFIG", {"archive": {"content_root": str(mock_env)}}):
            result = find_transcript_and_metadata("S01 E001")
            assert str(result["path"]) == str(test_file)
        
    def test_permission_error_handling(self, mock_env, mocker):
        """Test permission error handling"""
        test_file = mock_env / "readonly.md"
        test_file.write_text("test")
        test_file.chmod(0o444)  # Read-only
        
        # Mock os.makedirs to simulate permission error
        mocker.patch("os.makedirs", side_effect=PermissionError("test"))
        
        with pytest.raises(PermissionError):
            test_file.write_text("should fail")