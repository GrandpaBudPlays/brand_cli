from __future__ import annotations
from brand_cli.ai.gemini import GeminiModel
from brand_cli.transcript import Transcript
from brand_cli.workflow_context import WorkflowContext
from brand_cli.workflows.base import Workflow


class DescribeWorkflow(Workflow):
    """Placeholder for future Describe functionality."""
    
    def execute(self, context: WorkflowContext, model: GeminiModel) -> None:
        print("Starting Pass 3: Describe...")
        print("Describe functionality will be added later.")
