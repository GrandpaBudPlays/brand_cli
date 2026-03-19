from ai.gemini import GeminiModel
from file_manager import SessionData
from workflows.base import Workflow
from workflows.feedback import FeedbackWorkflow
from workflows.gold import GoldWorkflow


class AuditWorkflow(Workflow):
    """Generates both the Feedback and Gold reports."""
    
    def execute(self, session: SessionData, model: GeminiModel) -> None:
        file_obj = None
        try:
            # Upload the transcript once for all sub-workflows
            file_obj = model.upload_file(session.path, display_name=f"Transcript_{session.full_ep_id}")
            
            # Pass the file object to the session so child workflows can use it instead of raw text
            session.uploaded_file = file_obj
            
            # Run Feedback
            FeedbackWorkflow().execute(session, model)
            # Run Gold
            GoldWorkflow().execute(session, model)
            
            print("Audit workflow completed: Feedback and Gold reports generated.")
        finally:
            # Always clean up the remote file to prevent clutter, even if a workflow crashes
            if file_obj:
                model.delete_file(file_obj.name)
