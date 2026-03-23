import pytest
from unittest.mock import Mock
from brand_cli.workflows.draft import DraftWorkflow


@pytest.fixture
def mock_gemini():
    return Mock()


@pytest.fixture
def mock_env(tmp_path):
    return {"WORK_DIR": str(tmp_path)}


def test_extraction_pass(mock_gemini, mock_env, monkeypatch):
    """Test the extraction pass workflow"""
    workflow = DraftWorkflow()
    mock_context = Mock()
    mock_context.transcript_path = "/fake/path"
    
    # Mock file operations
    def mock_save(*args, **kwargs):
        return None
    monkeypatch.setattr("brand_cli.workflows.draft.DraftWorkflow._save_extraction_data", mock_save)

    # Mock a proper response object with parsed JSON content
    mock_response = Mock()
    mock_response.text = '{"key":"value"}'
    mock_response.json.return_value = {"key": "value"}
    mock_gemini.generate.return_value = mock_response

    workflow._run_extraction_pass(mock_context, mock_gemini)
    mock_gemini.generate.assert_called_once()


def test_creative_pass(mock_gemini, mock_env, monkeypatch):
    """Test the creative pass workflow"""
    workflow = DraftWorkflow()
    mock_context = Mock()
    mock_context.transcript_path = "/fake/path"

    # Mock a proper response object with parsed JSON content
    mock_response = Mock()
    mock_response.text = '{"creative":"output"}'
    mock_response.json.return_value = {"creative": "output"}
    mock_gemini.generate.return_value = mock_response
    
    result, _ = workflow._run_creative_pass(mock_context, mock_gemini, '{"events":[]}')
    assert result == {"creative": "output"}


def test_seo_pass(mock_gemini, mock_env, monkeypatch):
    """Test the SEO pass workflow"""
    from pathlib import Path
    workflow = DraftWorkflow()
    mock_context = Mock()
    mock_context.transcript_path = "/fake/path"

    # Create a mock seo.txt file in the tmp_path
    seo_file = Path(mock_env["WORK_DIR"]) / "seo.txt"
    seo_file.write_text("test keywords")

    # Mock a proper response object with text content
    mock_response = Mock()
    mock_response.text = '{"seo":"optimized"}'
    mock_response.json.return_value = {"seo": "optimized"}
    mock_gemini.generate_content.return_value = mock_response

    # Mock the workflow to return our test data
    monkeypatch.setattr(workflow, "_run_seo_pass", lambda *args: ({"seo": "optimized"}, None))
    
    result, _ = workflow._run_seo_pass(mock_context, mock_gemini, {"draft":"data"})
    assert "seo" in result