from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from brand_cli.workflow_context import WorkflowContext
    from brand_cli.ai.gemini import GeminiModel

class ChapterMixin:
    """
    Mixin for handling chapter extraction and management.
    Provides a standardized way to get or create chapters from a transcript.
    """

    def _get_or_create_chapters(self, context: 'WorkflowContext', model: 'GeminiModel') -> Dict[str, Any]:
        """
        Get or create chapters from the transcript.
        
        Args:
            context: The workflow context.
            model: The Gemini model for chapter extraction.
            
        Returns:
            A dictionary with the chapter data in the format:
            {"chapters": [{"timestamp": "00:00", "title": "Section Name"}]}
        """
        base_dir = Path(context.transcript_path).parent
        chapters_path = base_dir / "Extraction_Chapters.json"
        
        if chapters_path.exists():
            with open(chapters_path, "r", encoding="utf-8") as f:
                return json.load(f)
        
        # Trigger chapter extraction if the file doesn't exist
        result = model.generate(
            "Extract chapters from the transcript with timestamps and titles.",
            response_mime_type="application/json",
            file_obj=context.uploaded_file 
        )


        # Ensure the result is in the correct format
        raw_content = result.content if hasattr(result, 'content') else str(result)
        parsed_data = json.loads(raw_content)

        if isinstance(parsed_data, list):
            # If the AI gave us a direct list, wrap it
            chapters_list = parsed_data
        elif isinstance(parsed_data, dict):
            # If it's a dict, look for the 'chapters' key or the first list value found
            chapters_list = parsed_data.get("chapters", [])
        else:
            chapters_list = []

        chapters_data = {"chapters": chapters_list}
        
        # Save the chapters data
        chapters_path.parent.mkdir(parents=True, exist_ok=True)
        with open(chapters_path, "w", encoding="utf-8") as f:
            json.dump(chapters_data, f, indent=2)
        
        return chapters_data