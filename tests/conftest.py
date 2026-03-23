import pytest
from unittest.mock import Mock, MagicMock
from pathlib import Path
from brand_cli.workflow_context import WorkflowContext, Terminology

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
    (tmp_path / "audits").mkdir(parents=True, exist_ok=True)
    
    # Create context file
    context_file = tmp_path / ".brand_context"
    context_file.write_text("test_context")
    
    return tmp_path

@pytest.fixture
def integration_context(mock_env):
    """Fixture providing a real WorkflowContext with test data"""
    transcript_mock = Mock()
    
    # Extract the working directory from the mock_env fixture (Path or Dict)
    if isinstance(mock_env, dict):
        work_dir = Path(mock_env.get("WORK_DIR", "."))
    else:
        work_dir = Path(mock_env)
    
    return WorkflowContext(
        season="1",
        episode="5",
        full_ep_id="S01E05",
        target_filename="S01E05_Conrad.md",
        saga="Conrad",
        arc="The Awakening",
        transcript=transcript_mock,
        transcript_path=str(work_dir / "dummy.srt"),
        lexicon="standard",
        duration=1200.0,
        terms=Terminology()
    )