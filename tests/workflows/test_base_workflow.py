import pytest
import json
from unittest.mock import Mock
from pathlib import Path
from types import SimpleNamespace
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
        
    def test_process_json_saves_audit(self, integration_context, mock_gemini):
        """Test that JSON processing physically writes audit files to the sandbox"""
        class TestWorkflow(Workflow):
            def execute(self, context, model): pass
        
        workflow = TestWorkflow()
        # Use SimpleNamespace instead of Mock to bypass the 'skip audit' logic
        result = SimpleNamespace(
            success=True,
            content='{"test": "audit_data"}',
            model_name="test-model",
            error=None
        )

        # Ensure the directory exists
        transcript_path = Path(integration_context.transcript_path)
        transcript_path.parent.mkdir(parents=True, exist_ok=True)

        # Run the logic
        workflow._process_json_result(result, integration_context, "IntegrationTest")

        # Verify naming convention: "ReportName - ModelName-raw.json"
        transcript_dir = transcript_path.parent
        expected_file = "IntegrationTest - test-model-raw.json"
        
        assert (transcript_dir / expected_file).exists(), f"File not found. Found: {list(transcript_dir.iterdir())}"
        
        # Verify content matches
        with open(transcript_dir / expected_file) as f:
            assert json.loads(f.read()) == {"test": "audit_data"}

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
        assert "failed" in str(exc.value).lower() and "API error" in str(exc.value)
        
    def test_process_json_with_formatter(self, mock_env):
        """Test JSON processing with formatter function"""
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
        
        formatter = lambda data, ctx: f"Formatted: {data.get('test')}"
        data = workflow._process_json_result(
            mock_result, 
            mock_context, 
            "test-report",
            formatter
        )
        assert data == {"test": "data"}
        assert test_file.exists()