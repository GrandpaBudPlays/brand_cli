from __future__ import annotations
import os
import json
import yaml
from pathlib import Path
from typing import cast, Optional, Dict, Any, TYPE_CHECKING, Tuple, List
from brand_cli.ai.gemini import GeminiModel
from brand_cli.file_manager import save_audit_report, read_file, find_file_in_hierarchy
from brand_cli.prompts.loader import PromptLoader
from brand_cli.workflows.base import Workflow
from brand_cli.workflows.mixins import ChapterMixin
from brand_cli.fragments.tagged import TaggedExternalFragment
from brand_cli.fragments.random_plus import TextPlusRandom  


if TYPE_CHECKING:
    from brand_cli.workflow_context import WorkflowContext

class DraftWorkflow(ChapterMixin, Workflow):
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
        self._prompt_loader = PromptLoader()
        self._icon_map = None

    def execute(self, context: WorkflowContext, model: GeminiModel):
        pass_number = os.getenv("DRAFT_PASS", "1")
        self.logger.info(f"Executing Draft Workflow - Pass {pass_number}")
        
        # Pre-flight check: Draft workflow requires a preceding Gold report
        base_dir = Path(context.transcript_path).parent
        if not (base_dir / "Gold.md").exists():
            self.logger.error("Abort: Gold.md not found in episode folder.")
            print(f"Error: Gold report (Gold.md) not found in {base_dir}. Please run the 'gold' or 'audit' workflow first.")
            return

        try:
            if pass_number == "1":
                return self._run_extraction_pass(context, model)
            elif pass_number == "2":
                return self._run_creative_and_seo_pipeline(context, model)
            else:
                self.logger.error(f"Unknown pass number: {pass_number}")
                return None
        finally:
            # Cleanup transcript after extraction is complete
            if context.uploaded_file and pass_number == "1":
                self.logger.info("Cleaning up transcript after Pass 1")
                model.delete_file(context.uploaded_file)

    # --- Pipeline Coordination ---

    def _run_extraction_pass(self, context: WorkflowContext, model: GeminiModel) -> Optional[Dict[str, Any]]:
        """Handles Pass 1: Extracting factual events from the transcript."""
        print("--- Pass 1: Extraction ---")
        base_dir = Path(context.transcript_path).parent
        hints = read_file(str(base_dir / "hints.txt")) or ""
        
        self._get_or_create_chapters(context, model)

        prompt_data = self._prompt_loader.load_prompt(
            "draft_extraction",
            fragments={"hints": hints},
            session_data={
                "episode_id": context.full_ep_id,
                "lexicon": context.lexicon
            }
        )

        result = model.generate(
            prompt_data["user_prompt"],
            system_instruction=prompt_data["system_prompt"],
            temperature=0.4,
            response_mime_type="application/json",
            file_obj=context.uploaded_file
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
        assets = self._load_brand_assets(base_dir)
        self.logger.info(f"Loading extraction data from {extraction_path}")
        events_json = read_file(str(extraction_path))
        draft_data, creative_model = self._run_creative_pass(context, model, events_json, assets)
        
        if not draft_data:
            return

        # 2. SEO Pass (Optional)
        final_data, seo_model = self._run_seo_pass(context, model, draft_data, events_json, assets)

        # 3. Attempt to find and inject standard links.
        links_dir = find_file_in_hierarchy(Path(context.transcript_path), "Standard Link Repository.md")
        if links_dir:
            links_text = self._load_file_with_logging(links_dir, "Standard Link Repository.md", "Standard Link Repository")
            saga_tag = f"* **Saga {str(int(context.season.lstrip('S')))}"
            tagged_fragment = TaggedExternalFragment(raw_content=links_text, start_tag=saga_tag)
            final_data["standard_links"] = tagged_fragment.resolve() or "No standard links found for this season."
        else:
            self.logger.error(f"Standard Link Repository not found in hierarchy.")
            final_data["standard_links"] = f"No standard links found for this season."


        # 4. Attempt to find and inject the World Seed with randomization.
        seed_dir = find_file_in_hierarchy(Path(context.transcript_path), "World Seed.md")
        if seed_dir:
            seed_path = Path(seed_dir) / "World Seed.md"
            self.logger.info(f"Loaded World Seed from {seed_path}")
            seed_text = read_file(str(seed_path)) or ""
            seed_fragment = TextPlusRandom(raw_content=seed_text)
            final_data["world_seed"] = seed_fragment.resolve() or f"No world seed found at {seed_dir}."
        else:
            self.logger.error(f"No World Seed content found at {seed_dir}")
            final_data["world_seed"] = f"No World Seed content found at {seed_dir}"
        
        # 5. Final Assembly & Save
        final_md = self._build_markdown(draft_data, final_data, context, model)
        self._save_final_description(final_md, context)
        return final_md

    # --- Sub-Pass Logic ---

    def _run_creative_pass(self, context: WorkflowContext, model: GeminiModel, events_json: str, assets: Dict[str, str]) -> Tuple[dict, str]:
        """Pass 2: Injecting the Ulf, Grandpa, and Conrad voices into the factual events."""
        print("--- Pass 2: Creative Draft ---")
        base_dir = Path(context.transcript_path).parent
        
        # Load ledger_entry from Gold report to maintain voice consistency
        ledger_entry = ""
        # Look for the gold raw JSON (supports both new naming and legacy with model names)
        gold_json_path = next(base_dir.glob("Gold*raw.json"), None)

        if gold_json_path:
            try:
                with open(gold_json_path, "r", encoding="utf-8") as f:
                    gold_data = json.load(f)
                    ledger_entry = gold_data.get("ledger_entry", "")
                    if ledger_entry:
                        self.logger.info(f"Loaded ledger_entry from {gold_json_path.name}")
            except Exception as e:
                self.logger.error(f"Failed to load ledger from {gold_json_path}: {e}")

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
                "events_json": events_json,
                "ledger_entry": ledger_entry
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

    def _run_seo_pass(self, context: WorkflowContext, model: GeminiModel, draft_data: dict, events_json: str, assets: Dict[str, str]) -> Tuple[dict, Optional[str]]:
        """Pass 3: Optimizing the creative draft with SEO keywords if seo.txt exists."""
        # Try to load structured SEO config (Global first)
        seo_config = None
        try:
            seo_config = self._prompt_loader.load_config("seo")
        except Exception:
            pass

        if not seo_config:
            # Fallback to local episode directory seo.yaml
            base_dir = Path(context.transcript_path).parent
            local_seo = base_dir / "seo.yaml"
            if local_seo.exists():
                try:
                    with open(local_seo, "r", encoding="utf-8") as f:
                        seo_config = yaml.safe_load(f)
                except Exception as e:
                    self.logger.error(f"Failed to load local seo.yaml: {e}")

        if not seo_config:
            print("\n--- No seo.yaml found. Skipping SEO pass. ---")
            return draft_data, None

        print("\n--- Pass 3: SEO Injection ---")
        prompt_data = self._prompt_loader.load_prompt(
            "draft_seo",
            fragments={
                "narrative_keywords": ", ".join(seo_config.get("narrative_keywords", [])),
                "meta_tags": ", ".join(seo_config.get("meta_tags", [])),
                "lexicon": assets['lexicon'],
                "brand_voice": assets['grandpa'],
                "ulf_voice": assets['ulf']
            },
            session_data={
                "draft_json": json.dumps(draft_data),
                "events_json": events_json
            }
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

    def _icon_for_chapter(self, title: str) -> str:
        """Resolve a chapter icon based on chapter title keywords."""
        lower_title = (title or "").lower()

        # Lazy-load and cache the icon map once per workflow execution
        if self._icon_map is None:
            try:
                self._icon_map = self._prompt_loader.load_config("chapter_icons")
            except Exception as e:
                self.logger.error(f"Failed to load chapter_icons.yaml: {e}")
                self._icon_map = {}

        for icon, keywords in self._icon_map.items():
            if any(keyword in lower_title for keyword in keywords):
                return icon

        # Fallback to the default shield
        return "🛡️"

    def _format_chapters(self, chapters: List[Dict[str, Any]]) -> List[str]:
        """Format chapters as Markdown lines with icons."""
        formatted = []
        for chapter in chapters:
            timestamp = str(chapter.get("timestamp", "00:00")).strip()
            title = str(chapter.get("title", "Untitled")).strip()

            # Suppress leading 0: or 00: if hours is zero (e.g. 0:01:44 -> 01:44)
            parts = timestamp.split(':')
            if len(parts) == 3 and parts[0] in ('0', '00'):
                timestamp = ':'.join(parts[1:])

            icon = self._icon_for_chapter(title)
            formatted.append(f"{timestamp} {icon} {title}".strip())
        return formatted


    def _save_final_description(self, content: str, context: WorkflowContext) -> None:
        """Saves the human-readable Markdown to the episode directory."""
        save_audit_report(context.transcript_path, content, "Description")
        print("\nDraft Pipeline Complete.")

    def _build_markdown(self, draft_data: dict, final_data: dict, context: WorkflowContext, model: GeminiModel) -> str:
        """Assembles the final document with SEO fallbacks."""
        # Use SEO fields if available, otherwise use original draft fields
        ulf = final_data.get("ulf_hook_seo", final_data.get("ulf_hook", draft_data.get("ulf_hook", "")))
        chronicle = final_data.get("conrad_chronicle_seo", final_data.get("conrad_chronicle", draft_data.get("conrad_chronicle", "")))
        legend = final_data.get("grandpa_legend_seo", final_data.get("grandpa_legend", draft_data.get("grandpa_legend", "")))
        links = final_data.get("standard_links", draft_data.get("standard_links", "No Links Provided."))
        world_seed = final_data.get("world_seed", "No World Seed Provided.")
        tags = final_data.get("tags", [])

        # Get or create chapters
        chapters_data = self._get_or_create_chapters(context, model)
        chapters = chapters_data.get("chapters", [])
        formatted_chapters = self._format_chapters(chapters)
        
        # Resolve the external template using the established PromptLoader pattern
        assembly_data = self._prompt_loader.load_config("draft_assembly")
        template = assembly_data.get("template", "")

        return template.format(
            season=context.season,
            episode=context.episode,
            ulf=ulf,
            chronicle=chronicle,
            legend=legend,
            links=links,
            world_seed=world_seed,
            chapters="\n".join(formatted_chapters),
            seo_metadata=f"**Injected Tags:** {', '.join(tags)}" if tags else "*No SEO injection performed.*"
        )
    
    def _save_extraction_data(self, data: dict, context: WorkflowContext) -> None:
        """Saves a clean Extraction.json and a tracked audit version."""
        import json
        base_dir = Path(context.transcript_path).parent
        extraction_path = base_dir / "Extraction.json"

        # Save the clean version for Pass 2 to find
        with open(extraction_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    