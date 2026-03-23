import pytest
from brand_cli.ai.gemini import GeminiModel

class TestModelRunner:
    def test_mocked_generation(self, mock_gemini):
        """Test successful mocked generation"""
        mock_gemini("test response")
        model = GeminiModel()
        result = model.generate("test prompt")
        assert result.content == "test response"
        assert result.success is True

    def test_error_handling(self, mock_gemini):
        """Test error handling in generation"""
        # Configure mock to return error response instead of raising
        mock_result = mock_gemini()
        mock_result.success = False
        mock_result.error = "API error"
        
        model = GeminiModel()
        result = model.generate("test prompt")
        assert result.success is False
        assert "API error" in result.error