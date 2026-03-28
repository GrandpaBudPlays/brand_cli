import pytest
from unittest.mock import Mock, patch, MagicMock
from brand_cli.workflows.gold import GoldWorkflow, json_to_gold_markdown
from brand_cli.workflow_context import WorkflowContext

class TestJsonToGoldMarkdown:
    def test_full_formatting(self):
        """Test complete markdown structure generation"""
        test_data = {
            "summary_table": "Test Summary",
            "editors_notes": "Test Notes",
            "ledger_entry": "Test Narrative",
            "youtube_chapters": [{"time": "01:23", "title": "Intro"}],
            "type_a_shorts": [{"time": "02:34", "description": "Short Clip"}],
            "type_b_clips": [{"time": "03:45", "description": "Highlight"}],
            "type_c_arc": [{"time": "04:56", "description": "Milestone"}]
        }
        context = Mock(full_ep_id="TEST123")
        result = json_to_gold_markdown(test_data, context)
        assert "# 🛡️ Gold Extraction Report: TEST123" in result
        assert "## 📝 Summary Table" in result
        assert "## 🧠 Editor's Notes" in result
        assert "## 🪵 Ledger Entry" in result
        assert "## ⏱️ YouTube Chapters" in result
        assert "## 🎬 Type A (Shorts)" in result
        assert "## 📼 Type B (Clips)" in result
        assert "## ⚔️ Type C (Arc/Milestone Components)" in result

    def test_empty_lists(self):
        """Test handling of empty chapter/short lists"""
        test_data = {
            "summary_table": "",
            "editors_notes": "",
            "ledger_entry": "",
            "youtube_chapters": [],
            "type_a_shorts": [],
            "type_b_clips": [],
            "type_c_arc": []
        }
        context = Mock(full_ep_id="TEST123")
        result = json_to_gold_markdown(test_data, context)
        assert "- **00:00** - Intro" not in result  # No default entries for empty lists

class TestGoldWorkflow:
    @patch('brand_cli.ai.gemini.GeminiModel')
    def test_execute_happy_path(self, mock_model, tmp_path):
        """Test successful execution flow"""
        # Create a dummy file so Path().read_text() doesn't fail
        fake_chapters = tmp_path / "chapters.json"
        fake_chapters.write_text('{"chapters": []}')

        workflow = GoldWorkflow()
        context = Mock(
            transcript="test transcript",
            duration=3600,
            uploaded_file=None,
            transcript_path=str(tmp_path / "test_path"),
            chapters_path=str(fake_chapters)  # This stops the TypeError
        )
        
        mock_response = MagicMock(
            success=True,
            content='{"test": "data"}',
            model_name="test-model",
            error=None
        )
        mock_response.get.return_value = {"chapters": [{"timestamp": "00:00", "title": "Intro"}]}
        mock_model.generate.return_value = mock_response
    
        workflow.execute(context, mock_model)
        assert mock_model.generate.call_count == 2

    def test_missing_transcript(self):
        """Test handling of missing transcript"""
        workflow = GoldWorkflow()
        context = Mock(transcript=None)
        
        with patch('builtins.print') as mock_print:
            workflow.execute(context, Mock())
            mock_print.assert_called_with("No transcript available for gold extraction.")

    def test_malformed_response(self, tmp_path):
        """Test handling of invalid JSON response"""
        workflow = GoldWorkflow()
        context = Mock(
            transcript="test",
            transcript_path=str(tmp_path / "test_path"),
            duration=3600,  # Added numeric duration
            uploaded_file=None
        )
        mock_model = Mock()
        mock_response = Mock(
            success=True,
            content='invalid json',
            model_name="test-model",
            error=None
        )
        mock_response.get.side_effect = ValueError("Invalid JSON")
        mock_model.generate.return_value = mock_response
        
        with pytest.raises(ValueError):
            workflow.execute(context, mock_model)