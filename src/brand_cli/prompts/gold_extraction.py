from prompts.base import BasePrompt, PromptConfig


class GoldExtractionPrompt(BasePrompt):
    """Phase 2: Strategic Gold Extraction - Types A, B, C, D"""
    
    @property
    def name(self) -> str:
        return "gold_extraction"
    
    @property
    def config(self) -> PromptConfig:
        return PromptConfig(
            system_instruction=(
                "You are an expert Production Assistant and Content Analyst. "
                "CORE RULE: Apply the 'Brand Rule'—prioritize clear speech and helpful guidance. "
                "Avoid technical jargon unless relevant to the game. Focus on extracting the most engaging and valuable moments."
            ),
            user_template="""TASK: STRATEGIC HIGHLIGHT GOLD AUDIT

CATEGORIES:
- Type A (Shorts): 15-60s 'Lessons/Hooks' + On-Screen Hook.
- Type B (Clips): 1-5m Narrative beats + Strategic Rationale.
- Type C (Arc/Milestone Components): Atmospheric/Action montages + Theme.
- Type D (Timeline Map): YouTube Chapters. Start at 0:00. Pacing: {pacing}.
  CRITICAL YOUTUBE CHAPTER RULES:
  1. The first timestamp MUST be exactly "00:00"
  2. The first chapter MUST be named exactly "00:00 Intro" (or similar, but starting with 00:00).
  3. Chapters must be listed in chronological order.
  4. Chapters must be at least 10 seconds apart.
  5. Format timestamps as MM:SS (e.g., "05:12") or HH:MM:SS (e.g., "01:23:45"). NEVER use fractions or decimals (e.g., "05:12.500").

OUTPUT INSTRUCTIONS:
You must return a raw JSON object matching this structure:
{{
  "summary_table": "A brief overview of the episode's highlights.",
  "editors_notes": "Your strategic notes and rationale.",
  "ledger_entry": "A 150-300 word creative summary of the episode reflecting the brand's narrative voice.",
  "type_a_shorts": [
    {{"time": "MM:SS", "description": "Short description of the hook/lesson"}}
  ],
  "type_b_clips": [
    {{"time": "MM:SS", "description": "Narrative beat / rationale"}}
  ],
  "type_c_arc": [
    {{"time": "MM:SS", "description": "Theme / montage description"}}
  ],
  "youtube_chapters": [
    {{"time": "MM:SS", "title": "Chapter title"}}
  ]
}}

""",
            temperature=0.1,
            temperature_overrides={
                'gemini-3-flash-preview': 0.2,
                'gemini-2.5-flash': 0.2,
                'gpt-4o-mini': 0.25,
            }
        )

    
    def build_gold_prompt(
        self,
        duration_sec: float
    ) -> str:
        pacing = "High-density" if duration_sec < 1200 else "Strategic milestones"
        return self.build_prompt(
            pacing=pacing
        )
