import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from brand_cli.workflows.draft import DraftWorkflow
from brand_cli.workflow_context import WorkflowContext

@patch('brand_cli.workflows.draft.DraftWorkflow._run_creative_pass')
@patch('brand_cli.workflows.draft.DraftWorkflow._run_seo_pass')
@patch('brand_cli.workflows.draft.Path.exists')
@patch('brand_cli.fragments.random_plus.TextPlusRandom')
@patch('brand_cli.fragments.tagged.TaggedExternalFragment')
def test_link_injection_with_repository_missing(mock_tagged, mock_random, mock_exists, mock_seo_pass, mock_creative_pass, tmp_path):
        """Test link injection fallback when repository not found"""
        # Setup test context with all required parameters
        from types import SimpleNamespace
        
        context = WorkflowContext(
            season="1",
            episode="5",
            full_ep_id="S01E05",
            target_filename="test.md",
            transcript_path=str(tmp_path / "transcript.md"),
            saga="TestSaga",
            arc="TestArc",
            transcript="Test transcript content",
            lexicon={},
            duration=1200.0,
            terms=SimpleNamespace(
                ip="IP",
                series="Series",
                season="Season",
                arc="Arc"
            ),
            uploaded_file=None
        )
        
        workflow = DraftWorkflow()
    
        # Setup mocks
        mock_exists.return_value = True
        mock_creative_pass.return_value = ({"draft": "data"}, "model1")
        mock_seo_pass.return_value = ({"seo": "data"}, "model2")
    
        # Mock fragment classes
        mock_tagged.return_value.resolve.return_value = None
        mock_random.return_value.resolve.return_value = None
        
        # Create test files
        (tmp_path / "Extraction_Chapters.json").write_text('{"chapters": []}')
        
        # Mock path for TextPlusRandom
        mock_random.return_value.path = tmp_path / "world_seed"
    
        # Mock logger
        workflow.logger = MagicMock()
    
        # Mock save operations
        with patch("brand_cli.workflows.draft.DraftWorkflow._save_final_description"):
            with patch("brand_cli.workflows.draft.find_file_in_hierarchy", return_value=None):
                result = workflow._run_creative_and_seo_pipeline(context, Mock())
    
                assert "No standard links found for this season" in str(result)
                assert "🔗 Continue the Journey" in str(result)
                workflow.logger.error.assert_any_call("No World Seed content found at None")

@patch('brand_cli.workflows.draft.DraftWorkflow._run_creative_pass')
@patch('brand_cli.workflows.draft.DraftWorkflow._run_seo_pass')
@patch('brand_cli.workflows.draft.Path.exists')
@patch('brand_cli.fragments.random_plus.TextPlusRandom')
@patch('brand_cli.fragments.tagged.TaggedExternalFragment')
def test_world_seed_injection_with_file_found(mock_tagged, mock_random, mock_exists, mock_seo_pass, mock_creative_pass, tmp_path, monkeypatch):
        """Test world seed injection when file exists"""
        # Setup test context with all required parameters
        from types import SimpleNamespace
        
        context = WorkflowContext(
            season="1",
            episode="5",
            full_ep_id="S01E05",
            target_filename="test.md",
            transcript_path=str(tmp_path / "transcript.md"),
            saga="TestSaga",
            arc="TestArc",
            transcript="Test transcript content",
            lexicon={},
            duration=1200.0,
            terms=SimpleNamespace(
                ip="IP",
                series="Series",
                season="Season",
                arc="Arc"
            ),
            uploaded_file=None
        )
        
        workflow = DraftWorkflow()
    
        # Setup mocks
        mock_exists.return_value = True
        mock_creative_pass.return_value = ({"draft": "data"}, "model1")
        mock_seo_pass.return_value = ({"seo": "data"}, "model2")
    
        # Mock fragment classes
        mock_tagged.return_value.resolve.return_value = None
        mock_random.return_value.resolve.return_value = "Test world seed content"
        
        # Create test files
        seed_file = tmp_path / "World Seed.md"
        seed_file.write_text("Test content")
        
        extraction_file = tmp_path / "Extraction_Chapters.json"
        extraction_file.write_text('{"chapters": []}')
        
        # Mock path for TextPlusRandom
        mock_random.return_value.path = tmp_path / "world_seed"
    
        # Mock logger
        workflow.logger = MagicMock()
        
        # Mock to return the parent directory
        monkeypatch.setattr(
            "brand_cli.workflows.draft.find_file_in_hierarchy",
            lambda *args: tmp_path
        )
    
        # Mock save operations
        monkeypatch.setattr(workflow, "_save_final_description", lambda *args: None)
    
        result = workflow._run_creative_and_seo_pipeline(context, Mock())
        assert "No standard links found for this season" in str(result)
        assert "🪓 The Narrative" in str(result)
        workflow.logger.info.assert_any_call(f"Loaded World Seed from {str(tmp_path)}/World Seed.md")

@patch('brand_cli.workflows.draft.DraftWorkflow._run_creative_pass')
@patch('brand_cli.workflows.draft.DraftWorkflow._run_seo_pass')
@patch('brand_cli.workflows.draft.Path.exists')
@patch('brand_cli.fragments.random_plus.TextPlusRandom')
@patch('brand_cli.fragments.tagged.TaggedExternalFragment')
def test_world_seed_injection_with_file_missing(mock_tagged, mock_random, mock_exists, mock_seo_pass, mock_creative_pass, tmp_path):
        """Test world seed fallback when file missing"""
        # Setup test context with all required parameters
        from types import SimpleNamespace
        
        context = WorkflowContext(
            season="1",
            episode="5",
            full_ep_id="S01E05",
            target_filename="test.md",
            transcript_path=str(tmp_path / "transcript.md"),
            saga="TestSaga",
            arc="TestArc",
            transcript="Test transcript content",
            lexicon={},
            duration=1200.0,
            terms=SimpleNamespace(
                ip="IP",
                series="Series",
                season="Season",
                arc="Arc"
            ),
            uploaded_file=None
        )
        
        workflow = DraftWorkflow()
    
        # Setup mocks
        mock_exists.return_value = True
        mock_creative_pass.return_value = ({"draft": "data"}, "model1")
        mock_seo_pass.return_value = ({"seo": "data"}, "model2")
    
        # Mock fragment classes
        mock_tagged.return_value.resolve.return_value = None
        mock_random.return_value.resolve.return_value = None
        
        # Create test files
        (tmp_path / "Extraction_Chapters.json").write_text('{"chapters": []}')
        (tmp_path / "world_seed").mkdir()
        
        # Mock path for TextPlusRandom
        mock_random.return_value.path = tmp_path / "world_seed"
    
        # Mock logger
        workflow.logger = MagicMock()
    
        # Mock save operations
        with patch("brand_cli.workflows.draft.DraftWorkflow._save_final_description"):
            with patch("brand_cli.workflows.draft.find_file_in_hierarchy", return_value=None):
                result = workflow._run_creative_and_seo_pipeline(context, Mock())
    
            assert "[Ulf's Voice]" in str(result)
            assert "🪓 The Narrative" in str(result)
            workflow.logger.error.assert_called_with(f"No World Seed content found at None")