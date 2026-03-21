from abc import ABC, abstractmethod
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from brand_cli.ai.gemini import GeminiModel
    from brand_cli.workflow_context import WorkflowContext


class Workflow(ABC):
    """Base interface for all pipeline operations."""
    
    def __init__(self):
        self._owns_upload = False
    
    def _ensure_transcript_ready(self, context: 'WorkflowContext', model: 'GeminiModel') -> None:
        """Ensures transcript is uploaded to Gemini, reusing existing upload if available."""
        if context.uploaded_file:
            logging.info(f"[CLOUD] Reusing existing transcript ID: {context.uploaded_file.name}")
            return
            
        file_id = context.transcript_obj.ensure_uploaded(model)
        context.uploaded_file = file_id
        self._owns_upload = True
        logging.info(f"[CLOUD] Triggering fresh JIT upload for standalone run: {context.full_ep_id}")

    @abstractmethod
    def execute(self, context: 'WorkflowContext', model: 'GeminiModel') -> None:
        """Executes the specific workflow logic."""
        pass
