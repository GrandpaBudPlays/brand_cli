from __future__ import annotations
import logging
from brand_cli.ai.gemini import GeminiModel
from brand_cli.workflow_context import WorkflowContext
from brand_cli.workflows.base import Workflow
from brand_cli.workflows.feedback import FeedbackWorkflow
from brand_cli.workflows.gold import GoldWorkflow


class AuditWorkflow(Workflow):
    """Generates both the Feedback and Gold reports."""
    
    def execute(self, context: WorkflowContext, model: GeminiModel) -> None:
        try:
            # Upload transcript once for all sub-workflows
            context.uploaded_file = context.transcript.ensure_uploaded(model)
            logging.info(f"[CLOUD] Parent workflow managing transcript: {context.full_ep_id}")
            
            # Run sub-workflows
            FeedbackWorkflow().execute(context, model)
            GoldWorkflow().execute(context, model)
            
            print("Audit workflow completed: Feedback and Gold reports generated.")
        finally:
            # Clean up remote file
            if context.uploaded_file:
                logging.info(f"[CLOUD] Cleaning up parent-managed transcript: {context.full_ep_id}")
                model.delete_file(context.uploaded_file)
