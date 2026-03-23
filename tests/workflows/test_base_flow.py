import pytest
from pathlib import Path

class TestBaseFlow:
    def test_workflow_with_mocks(self, mock_gemini, mock_env):
        """Test workflow completes with mocked AI and file operations"""
        mock_gemini("test workflow response")
        
        # Example test - replace with actual workflow test
        output_file = mock_env / "output.txt"
        output_file.write_text("test content")
        
        assert output_file.exists()
        assert "test content" in output_file.read_text()