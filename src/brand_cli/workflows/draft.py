from __future__ import annotations
from multiprocessing import context
import os
import json
from pathlib import Path
from typing import cast, Optional, Dict, Any, TYPE_CHECKING, Tuple
from brand_cli.ai.gemini import GeminiModel
from brand_cli.file_manager import save_audit_report, read_file, find_file_in_hierarchy
from brand_cli.prompts.loader import PromptLoader
from brand_cli.workflows.base import Workflow
from brand_cli.fragments.tagged import TaggedExternalFragment
from brand_cli.fragments.random_plus import TextPlusRandom  


if TYPE_CHECKING:
    from brand_cli.workflow_context import WorkflowContext

class DraftWorkflow(Workflow):
    """
    The 4-pass Description Draft Pipeline.
    
    Pass 1: Factual Extraction (Transcript -> JSON)
    Pass 2: Creative Writing (JSON -> Narrative Draft)
    Pass 3: SEO Injection (Narrative Draft -> SEO Narrative)
    Pass 4: Final Assembly (Data -> Markdown)
    """

    def __init__(self):
        super().__init__()
        import logging
        self.logger = logging.getLogger(__name__)

    def execute(self, context: WorkflowContext, model: GeminiModel):
        pass_number = os.getenv("DRAFT_PASS", "1")
        self.logger.info(f"Executing Draft Workflow - Pass {pass_number}")

        if pass_number == "1":
            return self._run_extraction_pass(context, model)
        elif pass_number == "2":
            return self._run_creative_and_seo_pipeline(context, model)
        else:
            self.logger.error(f"Unknown pass number: {pass_number}")
            return None

    # --- Pipeline Coordination ---

    def _run_extraction_pass(self, context: WorkflowContext, model: GeminiModel) -> Optional[Dict[str, Any]]:
        """Handles Pass 1: Extracting factual events from the transcript."""
        print("--- Pass 1: Extraction ---")
        base_dir = Path(context.transcript_path).parent
        hints = read_file(str(base_dir / "hints.txt")) or ""
        
        loader = PromptLoader()

        # Uses helper to handle transcript upload/deletion
        result = self._generate_with_transcript(
            "draft_extraction", 
            loader, 
            context, 
            model,
            fragments={"hints": hints},
            session_data={
                "episode_id": context.full_ep_id,
                "lexicon": context.lexicon
            }
        )
        
        # Save raw JSON for Pass 2 to consume
        data = self._process_json_result(result, context, "Extraction")
        
        # Use the helper to ensure Extraction.json exists
        self._save_extraction_data(data, context)

        print(f"\nPass 1 Complete! Review Extraction.json in {base_dir}")
        print("To continue to Pass 2 (Creative Writing), run with '--continue'")
        return data

    def _run_creative_and_seo_pipeline(self, context: WorkflowContext, model: GeminiModel):
        """Coordinates Pass 2 (Creative) and Pass 3 (SEO) into a single logical flow."""
        base_dir = Path(context.transcript_path).parent
        extraction_path = base_dir / "Extraction.json"

        if not extraction_path.exists():
            print(f"Error: Extraction.json not found. Run Pass 1 first.")
            return

        # 1. Creative Pass
        self.logger.info(f"Loading extraction data from {extraction_path}")
        events_json = read_file(str(extraction_path))
        draft_data, creative_model = self._run_creative_pass(context, model, events_json)
        
        if not draft_data:
            return

        # 2. SEO Pass (Optional)
        final_data, seo_model = self._run_seo_pass(context, model, draft_data)

        # 3. Attempt to find and inject standard links.
        links_dir = find_file_in_hierarchy(Path(context.transcript_path), "Standard Link Repository.md")
        if links_dir:
            links_text = self._load_file_with_logging(links_dir, "Standard Link Repository.md", "Standard Link Repository")
            saga_tag = f"* **Saga {str(int(context.season.lstrip('S')))}"
            tagged_fragment = TaggedExternalFragment(raw_content=links_text, start_tag=saga_tag)
            final_data["standard_links"] = tagged_fragment.resolve() or "No standard links found for this season."
        else:
            self.logger.error(f"No World Seed content found at {links_dir}")
            final_data["standard_links"] = f"No standard links found for this season."


        # 4. Attempt to find and inject the World Seed with randomization.
        seed_dir = find_file_in_hierarchy(Path(context.transcript_path), "World Seed.md")
        if seed_dir:
            seed_text = self._load_file_with_logging(Path(seed_dir), "World Seed.md", "World Seed")
            seed_fragment = TextPlusRandom(raw_content=seed_text)
            final_data["world_seed"] = seed_fragment.resolve() or "No world seed found."
        else:
            self.logger.error(f"No World Seed content found at {seed_dir}")
            final_data["world_seed"] = f"No World Seed content found at {seed_dir}"
        
        # 5. Final Assembly & Save
        # Use the name of the last model to successfully touch the data
        attribution_model = seo_model if seo_model else creative_model
        
        final_md = self._build_markdown(draft_data, final_data, context)
        self._save_final_description(final_md, context, attribution_model)
        return final_md

    # --- Sub-Pass Logic ---

    def _run_creative_pass(self, context: WorkflowContext, model: GeminiModel, events_json: str) -> Tuple[dict, str]:
        """Pass 2: Injecting the Ulf, Grandpa, and Conrad voices into the factual events."""
        print("--- Pass 2: Creative Draft ---")
        base_dir = Path(context.transcript_path).parent
        assets = self._load_brand_assets(base_dir)
        
        loader = PromptLoader()
        prompt_data = loader.load_prompt(
            "draft_creative",
            fragments={
                "series_metadata": assets['series'],
                "ulf_persona": assets['ulf'],
                "descriptions_protocol": assets['protocol'],
                "lexicon": assets['lexicon'],
                "grandpa_voice": assets['grandpa'] 
            },
            session_data={
                "game": "valheim",
                "events_json": events_json
            }
        )
        prompt = prompt_data["user_prompt"]
            
        result = model.generate(
            prompt,
            system_instruction=prompt_data["system_prompt"],
            temperature=0.4,
            response_mime_type="application/json"
        )
        
        data = self._process_json_result(result, context, "Draft")
        return data, result.model_name

    def _run_seo_pass(self, context: WorkflowContext, model: GeminiModel, draft_data: dict) -> Tuple[dict, Optional[str]]:
        """Pass 3: Optimizing the creative draft with SEO keywords if seo.txt exists."""
        base_dir = Path(context.transcript_path).parent
        seo_keywords = read_file(str(base_dir / "seo.txt"))
        
        if not seo_keywords:
            print("\n--- No seo.txt found. Skipping SEO pass. ---")
            return draft_data, None

        print("\n--- Pass 3: SEO Injection ---")
        loader = PromptLoader()
        prompt_data = loader.load_prompt(
            "draft_seo",
            fragments={"seo_keywords": seo_keywords},
            session_data={"draft_json": json.dumps(draft_data)}
        )
        prompt = prompt_data["user_prompt"]
        
        result = model.generate(
            prompt,
            system_instruction=prompt_data["system_prompt"],
            temperature=0.1,
            response_mime_type="application/json"
        )
        
        data = self._process_json_result(result, context, "Draft-SEO")
        return data, result.model_name

    # --- Shared Helpers ---

    def _load_file_with_logging(self, path: str, file_name: str, description: str) -> str:
        """Helper to load a file and log success/failure."""

        file_path = str(path / file_name)
        content = read_file(file_path)
        if content:
            self.logger.info(f"Loaded {description} from {file_path}")
        else:
            self.logger.error(f"{description} not found at {file_path}")
        return content or ""

    def _load_brand_assets(self, base_dir: Path) -> Dict[str, str]:
        """Climbs the directory tree to find Ulf's Persona, the Protocol, and Brand Context."""
     
        archive_root = find_file_in_hierarchy(base_dir, ".series_metadata") or base_dir
        ip_root = find_file_in_hierarchy(base_dir, "Descriptions.md") or base_dir
        arc_dir = find_file_in_hierarchy(base_dir, "Ulf Persona.md") or base_dir
        global_core_dir = archive_root / "000-Global-Core"
        if not (global_core_dir / "Brand-Voice.md").exists():
            global_core_dir = base_dir

        grandpa_content = self._load_file_with_logging(global_core_dir, "Brand-Voice.md", "Grandpa")
        protocol_content = self._load_file_with_logging(ip_root, "Descriptions.md", "Descriptions Protocol")
        lexicon_content = self._load_file_with_logging(ip_root, "Saga-Lexicon-Valheim.md", "Lexicon")
        ulf_content = self._load_file_with_logging(arc_dir, "Ulf Persona.md", "Ulf Persona")
        series_metadata = self._load_file_with_logging(archive_root, ".series_metadata", "Series Metadata")

        return {
            "ulf": ulf_content,
            "protocol": protocol_content,
            "series": series_metadata,
            "lexicon": lexicon_content,
            "grandpa": grandpa_content
        }

    def _generate_with_transcript(self, template_name: str, loader: PromptLoader, context: WorkflowContext, model: GeminiModel, session_data: Dict[str, Any] = None, fragments: Dict[str, Any] = None):
        """Standardizes the temporary upload and cleanup of the transcript file."""
        file_obj = None
        try:
            file_obj = model.upload_file(
                context.transcript_path, 
                display_name=f"TS_{context.full_ep_id}"
            )
            prompt_data = loader.load_prompt(
                template_name,
                session_data=session_data,
                fragments=fragments
            )
            return model.generate(
                prompt_data["user_prompt"],
                system_instruction=prompt_data["system_prompt"],
                temperature=0.4,
                response_mime_type="application/json",
                file_obj=file_obj
            )
        finally:
            if file_obj:
                model.delete_file(file_obj.name)

    def _save_final_description(self, content: str, context: WorkflowContext, model_name: str) -> None:
        """Saves the human-readable Markdown to the episode directory."""
        save_audit_report(context.transcript_path, content, "Description", model_name)
        print("\nDraft Pipeline Complete.")

    def _build_markdown(self, draft_data: dict, final_data: dict, context: WorkflowContext) -> str:
        """Assembles the final document with SEO fallbacks."""
        # Use SEO fields if available, otherwise use original draft fields
        ulf = final_data.get("ulf_hook_seo", final_data.get("ulf_hook", draft_data.get("ulf_hook", "")))
        legend = final_data.get("grandpa_legend_seo", final_data.get("grandpa_legend", draft_data.get("grandpa_legend", "")))
        chronicle = final_data.get("conrad_chronicle_seo", final_data.get("conrad_chronicle", draft_data.get("conrad_chronicle", "")))
        links = final_data.get("standard_links", draft_data.get("standard_links", "No Links Provided."))
        tags = final_data.get("tags", [])

        md = f"# 📝 Triple-Threat Description: {context.season} {context.episode}\n\n"
        md += "## 🪓 The Narrative\n\n"
        md += f"**[Ulf's Voice]**\n{ulf}\n\n"
        md += f"**[Grandpa's Legend]**\n{legend}\n\n"
        md += f"**[Conrad's Chronicle]**\n{chronicle}\n\n"
        md += "---\n\n"
        md += "## 🔗 Continue the Journey\n"
        md += f"{links}\n\n"
        md += "## 🏷️ SEO & Metadata\n"
        md += f"**Injected Tags:** {', '.join(tags)}" if tags else "*No SEO injection performed.*"
        return md
    
    def _save_extraction_data(self, data: dict, context: WorkflowContext) -> None:
        """Saves a clean Extraction.json and a tracked audit version."""
        import json
        base_dir = Path(context.transcript_path).parent
        extraction_path = base_dir / "Extraction.json"

        # Save the clean version for Pass 2 to find
        with open(extraction_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    