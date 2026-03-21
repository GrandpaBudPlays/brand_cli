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
            session.uploaded_file = context.transcript_obj.ensure_uploaded(model)
            logging.info(f"[CLOUD] Parent workflow managing transcript: {session.full_ep_id}")
            
            # Run sub-workflows
            FeedbackWorkflow().execute(session, model)
            GoldWorkflow().execute(session, model)
            
            print("Audit workflow completed: Feedback and Gold reports generated.")
        finally:
            # Clean up remote file
            if session.uploaded_file:
                logging.info(f"[CLOUD] Cleaning up parent-managed transcript: {session.full_ep_id}")
                model.delete_file(session.uploaded_file)
