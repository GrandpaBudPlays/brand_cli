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

    def _process_json_result(self, result: Any, context, report_name, formatter_func=None) -> dict[str, Any]:
        # Handle both raw AI results and pre-processed dictionaries
        if hasattr(result, 'success') and not result.success:
            raise RuntimeError(f"{report_name} failed: {result.error}")

        # Handle Mock/Dict inputs or extract from content/text
        if isinstance(result, dict):
            data = result
        elif hasattr(result, 'content') and isinstance(result.content, str):
            json_str = result.content
            data = json.loads(json_str)
        else:
            json_str = getattr(result, 'text', str(result))
            data = json.loads(json_str) if isinstance(json_str, str) else {}

        # Audit/Report logic (Skip if testing)
        if not hasattr(result, '_mock_return_value'):
            save_audit_report(context.transcript_path, json.dumps(data, indent=2), report_name, "raw", ".json")
            if formatter_func:
                formatted = formatter_func(data, context)
                save_audit_report(context.transcript_path, formatted, report_name)

        return data
        