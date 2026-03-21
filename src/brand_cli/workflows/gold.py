import json
from typing import cast
from brand_cli.ai.gemini import GeminiModel
from brand_cli.file_manager import save_audit_report, SessionData
from brand_cli.transcript import Transcript
from brand_cli.prompts import get_prompt_library
from brand_cli.prompts.gold_extraction import GoldExtractionPrompt
from brand_cli.workflows.base import Workflow


def json_to_gold_markdown(data: dict, session: SessionData) -> str:
    md = f"# 🛡️ Gold Extraction Report: {session.full_ep_id}\n\n"
    
    md += f"## 📝 Summary Table\n{data.get('summary_table', '')}\n\n"
    md += f"## 🧠 Editor's Notes\n{data.get('editors_notes', '')}\n\n"
    
    md += "## 🪵 Ledger Entry (Narrative Summary)\n"
    md += f"> {data.get('ledger_entry', '')}\n\n"
    
    md += "## ⏱️ YouTube Chapters\n"
    for chap in data.get('youtube_chapters', []):
        md += f"- **{chap.get('time', '00:00')}** - {chap.get('title', 'Intro')}\n"
    md += "\n"
    
    md += "## 🎬 Type A (Shorts)\n"
    for short in data.get('type_a_shorts', []):
        md += f"- **{short.get('time', '00:00')}**: {short.get('description', '')}\n"
    md += "\n"
    
    md += "## 📼 Type B (Clips)\n"
    for clip in data.get('type_b_clips', []):
        md += f"- **{clip.get('time', '00:00')}**: {clip.get('description', '')}\n"
    md += "\n"
    
    md += "## ⚔️ Type C (Arc/Milestone Components)\n"
    for arc_comp in data.get('type_c_arc', []):
        md += f"- **{arc_comp.get('time', '00:00')}**: {arc_comp.get('description', '')}\n"
    md += "\n"
    
    return md


class GoldWorkflow(Workflow):
    """Generates the strategic gold extraction report."""
    
    def execute(self, session: SessionData, model: GeminiModel) -> None:
        print("Starting Strategic Gold Extraction...")
        
        prompts = get_prompt_library("valheim")
        gold_prompt: GoldExtractionPrompt = cast(GoldExtractionPrompt, prompts.get("gold_extraction"))
        
        prompt = gold_prompt.build_gold_prompt(duration_sec=session.duration)
        
        temperature = gold_prompt.get_temperature(model.name)
        result = model.generate(
            prompt,
            system_instruction=gold_prompt.get_system_instruction(),
            temperature=temperature,
            response_mime_type="application/json",
            file_obj=session.uploaded_file
        )
        
        if not result.success:
            raise RuntimeError(f"Failed to generate strategic gold content: {result.error}")
        
        try:
            data = json.loads(result.content)
            markdown_content = json_to_gold_markdown(data, session)
            
            # Save raw JSON for debugging and automation
            save_audit_report(session.path, json.dumps(data, indent=2), "Gold", f"{result.model_name}-raw", ".json")
            # Save human-readable Markdown
            save_audit_report(session.path, markdown_content, "Gold", result.model_name)
        except json.JSONDecodeError as e:
            print(f"JSON decode failed for Gold Extraction. Falling back to raw text. Error: {e}")
            save_audit_report(session.path, result.content, "Gold", result.model_name)
            
        print("Gold Extraction Complete.")
