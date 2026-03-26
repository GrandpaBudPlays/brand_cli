import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from brand_cli.workflows.draft import DraftWorkflow

@patch('brand_cli.workflows.draft.DraftWorkflow._run_creative_pass')
@patch('brand_cli.workflows.draft.DraftWorkflow._run_seo_pass')
@patch('brand_cli.workflows.draft.Path.exists')
@patch('brand_cli.fragments.random_plus.TextPlusRandom')
@patch('brand_cli.fragments.tagged.TaggedExternalFragment')
def test_link_injection_with_repository_found(mock_tagged, mock_random, mock_exists, mock_seo_pass, mock_creative_pass, integration_context, monkeypatch):
        """Test link injection when Standard Link Repository exists"""
        workflow = DraftWorkflow()
    
        # Setup mocks
        mock_exists.return_value = True
        mock_creative_pass.return_value = ({"draft": "data"}, "model1")
        mock_seo_pass.return_value = ({"seo": "data"}, "model2")
    
        # Mock fragment classes
        mock_tagged.return_value.resolve.return_value = "[Saga 1](link1)\n[Saga 2](link2)"
        mock_random.return_value.resolve.return_value = "Test world seed content"
        
        # Mock path for TextPlusRandom
        mock_random.return_value.path = Path("/mock/world_seed")
    
        # Mock file operations
        monkeypatch.setattr(
            "brand_cli.workflows.draft.find_file_in_hierarchy",
            lambda *args: Path("/mock/links")
        )
    
        # Mock logger
        workflow.logger = MagicMock()
    
        # Mock save operations
        monkeypatch.setattr(workflow, "_save_final_description", lambda *args: None)
    
        result = workflow._run_creative_and_seo_pipeline(integration_context, Mock())
        assert "[Saga 1](link1)" in result
        assert "Continue the Journey" in result

@patch('brand_cli.workflows.draft.DraftWorkflow._run_creative_pass')
@patch('brand_cli.workflows.draft.DraftWorkflow._run_seo_pass')
@patch('brand_cli.workflows.draft.Path.exists')
@patch('brand_cli.fragments.random_plus.TextPlusRandom')
@patch('brand_cli.fragments.tagged.TaggedExternalFragment')
def test_link_injection_with_repository_missing(mock_tagged, mock_random, mock_exists, mock_seo_pass, mock_creative_pass, integration_context):
        """Test link injection fallback when repository not found"""
        workflow = DraftWorkflow()
    
        # Setup mocks
        mock_exists.return_value = True
        mock_creative_pass.return_value = ({"draft": "data"}, "model1")
        mock_seo_pass.return_value = ({"seo": "data"}, "model2")
    
        # Mock fragment classes
        mock_tagged.return_value.resolve.return_value = None
        mock_random.return_value.resolve.return_value = None
        
        # Mock path for TextPlusRandom
        mock_random.return_value.path = Path("/mock/world_seed")
    
        # Mock logger
        workflow.logger = MagicMock()
    
        # Mock save operations
        with patch("brand_cli.workflows.draft.DraftWorkflow._save_final_description"):
            with patch("brand_cli.workflows.draft.find_file_in_hierarchy", return_value=None):
                result = workflow._run_creative_and_seo_pipeline(integration_context, Mock())
    
            assert "No Links Provided" in result
            assert "Continue the Journey" in result
            workflow.logger.error.assert_called_with("Standard Link Repository not found at /mock/links")

@patch('brand_cli.workflows.draft.DraftWorkflow._run_creative_pass')
@patch('brand_cli.workflows.draft.DraftWorkflow._run_seo_pass')
@patch('brand_cli.workflows.draft.Path.exists')
@patch('brand_cli.fragments.random_plus.TextPlusRandom')
@patch('brand_cli.fragments.tagged.TaggedExternalFragment')
def test_world_seed_injection_with_file_found(mock_tagged, mock_random, mock_exists, mock_seo_pass, mock_creative_pass, integration_context, monkeypatch):
        """Test world seed injection when file exists"""
        workflow = DraftWorkflow()
    
        # Setup mocks
        mock_exists.return_value = True
        mock_creative_pass.return_value = ({"draft": "data"}, "model1")
        mock_seo_pass.return_value = ({"seo": "data"}, "model2")
    
        # Mock fragment classes
        mock_tagged.return_value.resolve.return_value = None
        mock_random.return_value.resolve.return_value = "Test world seed content"
        
        # Mock path for TextPlusRandom
        mock_random.return_value.path = Path("/mock/world_seed")
    
        # Mock logger
        workflow.logger = MagicMock()
    
        # Mock file operations
        monkeypatch.setattr(
            "brand_cli.workflows.draft.find_file_in_hierarchy",
            lambda *args: Path("/mock/world_seed")
        )
    
        # Mock save operations
        monkeypatch.setattr(workflow, "_save_final_description", lambda *args: None)
    
        result = workflow._run_creative_and_seo_pipeline(integration_context, Mock())
        assert "Test world seed content" in result
        assert "The Narrative" in result
        workflow.logger.info.assert_called_with("Loaded World Seed from /mock/world_seed/World Seed.md")

@patch('brand_cli.workflows.draft.DraftWorkflow._run_creative_pass')
@patch('brand_cli.workflows.draft.DraftWorkflow._run_seo_pass')
@patch('brand_cli.workflows.draft.Path.exists')
@patch('brand_cli.fragments.random_plus.TextPlusRandom')
@patch('brand_cli.fragments.tagged.TaggedExternalFragment')
def test_world_seed_injection_with_file_missing(mock_tagged, mock_random, mock_exists, mock_seo_pass, mock_creative_pass, integration_context):
        """Test world seed fallback when file missing"""
        workflow = DraftWorkflow()
    
        # Setup mocks
        mock_exists.return_value = True
        mock_creative_pass.return_value = ({"draft": "data"}, "model1")
        mock_seo_pass.return_value = ({"seo": "data"}, "model2")
    
        # Mock fragment classes
        mock_tagged.return_value.resolve.return_value = None
        mock_random.return_value.resolve.return_value = None
        
        # Mock path for TextPlusRandom
        mock_random.return_value.path = Path("/mock/world_seed")
    
        # Mock logger
        workflow.logger = MagicMock()
    
        # Mock save operations
        with patch("brand_cli.workflows.draft.DraftWorkflow._save_final_description"):
            with patch("brand_cli.workflows.draft.find_file_in_hierarchy", return_value=None):
                result = workflow._run_creative_and_seo_pipeline(integration_context, Mock())
    
            assert "No world seed content" in result
            assert "The Narrative" in result
            workflow.logger.error.assert_called_with("World Seed not found at /mock/world_seed/World Seed.md")