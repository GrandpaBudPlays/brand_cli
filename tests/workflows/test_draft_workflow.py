import pytest
import json
from unittest.mock import Mock
from brand_cli.workflows.draft import DraftWorkflow


@pytest.fixture
def mock_gemini():
    return Mock()


@pytest.fixture
def mock_env(tmp_path):
    return {"WORK_DIR": str(tmp_path)}


def test_extraction_pass(mock_gemini, integration_context, monkeypatch):
    """Test the extraction pass workflow"""
    workflow = DraftWorkflow()
    
    # Mock file operations
    def mock_save(*args, **kwargs):
        return None
    monkeypatch.setattr("brand_cli.workflows.draft.DraftWorkflow._save_extraction_data", mock_save)

    # Mock a proper response object with parsed JSON content
    mock_response = Mock()
    mock_response.text = '{"events": [{"timestamp": "00:01", "event": "Conrad finds a hidden cave"}]}'
    mock_response.json.return_value = {"events": [{"timestamp": "00:01", "event": "Conrad finds a hidden cave"}]}
    mock_gemini.generate.return_value = mock_response

    result = workflow._run_extraction_pass(integration_context, mock_gemini)
    mock_gemini.generate.assert_called_once()
    assert result == {"events": [{"timestamp": "00:01", "event": "Conrad finds a hidden cave"}]}


def test_workflow_pass_chaining(mock_gemini, integration_context, monkeypatch):
    """Test data flows correctly between passes"""
    workflow = DraftWorkflow()
    
    # Mock extraction pass response
    mock_extraction_response = Mock()
    mock_extraction_response.text = '{"events": [{"timestamp": "00:01", "event": "Conrad finds a hidden cave"}]}'
    mock_extraction_response.json.return_value = {"events": [{"timestamp": "00:01", "event": "Conrad finds a hidden cave"}]}
    
    # Mock creative pass response
    mock_creative_response = Mock()
    mock_creative_response.text = '{"creative": "output"}'
    mock_creative_response.json.return_value = {"creative": "output"}
    
    # Setup mock to return different responses for each call
    mock_gemini.generate.side_effect = [mock_extraction_response, mock_creative_response]
    
    # Run workflow passes
    extraction_data = workflow._run_extraction_pass(integration_context, mock_gemini)
    creative_result, _ = workflow._run_creative_pass(integration_context, mock_gemini, json.dumps(extraction_data))
    
    # Verify creative pass received extraction data
    assert mock_gemini.generate.call_count == 2
    assert creative_result == {"creative": "output"}
    assert "Conrad finds a hidden cave" in str(mock_gemini.generate.call_args_list[1])


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
    
def test_draft_formatter_integration(integration_context, mock_gemini, monkeypatch):
    """Test draft workflow formatter integration"""
    from pathlib import Path
    
    # Force Pass 2 execution
    monkeypatch.setenv("DRAFT_PASS", "2")
    
    # Create sample Extraction.json for Pass 2 to read
    extraction_path = Path(integration_context.transcript_path).parent / "Extraction.json"
    extraction_path.write_text('{"events": [{"timestamp": "00:01", "event": "Conrad finds a hidden cave"}]}')
    
    workflow = DraftWorkflow()
    
    # Mock creative pass response
    mock_creative = Mock()
    mock_creative.text = '{"ulf_hook": "Ulf intro", "grandpa_legend": "Grandpa story", "conrad_chronicle": "Conrad finds cave"}'
    mock_creative.json.return_value = {"ulf_hook": "Ulf intro", "grandpa_legend": "Grandpa story", "conrad_chronicle": "Conrad finds cave"}
    mock_gemini.generate.return_value = mock_creative
    
    # Run workflow
    result = workflow.execute(integration_context, mock_gemini)
    
    # Verify final markdown contains expected sections
    assert "## 🪓 The Narrative" in result
    assert "[Ulf's Voice]" in result
    assert "[Grandpa's Legend]" in result
    assert "[Conrad's Chronicle]" in result