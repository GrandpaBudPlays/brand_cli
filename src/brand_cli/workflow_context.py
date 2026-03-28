from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Terminology:
    ip: str = "IP"
    series: str = "Series"
    season: str = "Season"
    arc: str = "Arc"

@dataclass
class WorkflowContext:
    season: str
    episode: str
    full_ep_id: str
    target_filename: str
    saga: str
    arc: str
    transcript: 'Transcript'
    transcript_path: str
    lexicon: str
    duration: float
    terms: Terminology
    uploaded_file: Optional[Any] = None
    chapters_path: Optional[str] = None  # Path to Extraction_Chapters.json
    force: bool = False  # CLI flag for idempotency bypass