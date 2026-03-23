import pytest
from unittest.mock import Mock, MagicMock
from pathlib import Path

@pytest.fixture
def mock_gemini(mocker):
    """Fixture to mock Gemini.generate() with configurable responses"""
    mock_result = MagicMock()
    mock_result.content = "mocked response"
    mock_result.success = True
    mock_result.input_tokens = 100
    mock_result.output_tokens = 50
    mock_result.cost = 0.0
    mock_result.fallback_used = False
    
    def configure_mock(return_value=None, error=None):
        if error:
            mocker.patch(
                "brand_cli.ai.gemini.GeminiModel.generate",
                side_effect=error
            )
        else:
            if return_value:
                mock_result.content = return_value
            mocker.patch(
                "brand_cli.ai.gemini.GeminiModel.generate",
                return_value=mock_result
            )
        return mock_result
    
    return configure_mock

@pytest.fixture
def mock_env(tmp_path):
    """Fixture to create mock environment structure"""
    # Create required directories
    (tmp_path / "audits").mkdir()
    
    # Create context file
    context_file = tmp_path / ".brand_context"
    context_file.write_text("test_context")
    
    return tmp_path