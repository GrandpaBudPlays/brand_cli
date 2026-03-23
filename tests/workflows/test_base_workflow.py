import pytest
from unittest.mock import Mock
from brand_cli.workflows.base import Workflow
from brand_cli.workflow_context import WorkflowContext

class TestBaseWorkflow:
    def test_execute_abstract(self):
        """Test Workflow is abstract"""
        with pytest.raises(TypeError) as exc:
            Workflow()
        assert "abstract" in str(exc.value)
            
    def test_process_json_success(self, mock_env):
        """Test JSON processing with valid data"""
        class TestWorkflow(Workflow):
            def execute(self, context, model): pass
            
        workflow = TestWorkflow()
        mock_result = Mock(
            success=True,
            content='{"test": "data"}',
            model_name="test-model",
            error=None
        )
        test_file = mock_env / "test.md"
        test_file.write_text("test")
        mock_context = Mock(transcript_path=str(test_file))
        
        data = workflow._process_json_result(
            mock_result, 
            mock_context, 
            "test-report",
            lambda d, ctx: "formatted"
        )
        assert data == {"test": "data"}
        assert test_file.exists()

    def test_process_json_failure(self):
        """Test error handling in JSON processing"""
        class TestWorkflow(Workflow):
            def execute(self, context, model): pass
            
        workflow = TestWorkflow()
        mock_result = Mock(
            success=False,
            error="API error"
        )
        
        with pytest.raises(RuntimeError) as exc:
            workflow._process_json_result(mock_result, Mock(), "test")
        assert "Failed to generate" in str(exc.value)