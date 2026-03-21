from abc import ABC, abstractmethod
import json
from typing import TYPE_CHECKING, Callable, Any
from brand_cli.file_manager import save_audit_report

if TYPE_CHECKING:
    from brand_cli.workflow_context import WorkflowContext
    from brand_cli.ai.gemini import GeminiModel

class Workflow(ABC):
    @abstractmethod
    def execute(self, context: 'WorkflowContext', model: 'GeminiModel') -> None:
        """Executes the specific workflow logic."""
        pass

    def _process_json_result(self, result, context, report_name, formatter_func=None) -> dict:
        if not result.success:
            raise RuntimeError(f"Failed to generate {report_name}: {result.error}")
        
        try:
            data = json.loads(result.content)
            # Save raw JSON
            save_audit_report(context.transcript_path, json.dumps(data, indent=2), report_name, f"{result.model_name}-raw", ".json")
            
            if formatter_func:
                markdown_content = formatter_func(data, context)
                save_audit_report(context.transcript_path, markdown_content, report_name, result.model_name)
            
            return data # Return the data for multi-pass workflows
                
        except json.JSONDecodeError as e:
            print(f"JSON decode failed for {report_name}. Falling back to raw text. Error: {e}")
            save_audit_report(context.transcript_path, result.content, report_name, result.model_name)
            return {}
        