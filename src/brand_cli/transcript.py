import re
import logging
from typing import Optional
from brand_cli.ai.gemini import GeminiModel
from brand_cli.utils import read_file


class Transcript:
    def __init__(self, raw_content: str, episode_id: str):
        """Initialize with raw content instead of file path"""
        self._content = raw_content
        self.episode_id = episode_id
        self.file_id: Optional[str] = None

    def _has_no_audio(self) -> bool:
        if not self._content:
            return False
        header_chunk = self._content[:500]
        if "no audio" in header_chunk.lower():
            return not bool(re.search(r'\d{1,2}:\d{2}', header_chunk))
        return False

    def get_content(self) -> str:
        """Returns the raw transcript content"""
        if not self._content:
            logging.warning(f"[SKIP] {self.episode_id}: Empty transcript")
            raise ValueError(f"{self.episode_id}: Empty transcript")
        if self._has_no_audio():
            logging.warning(f"[SKIP] {self.episode_id}: No Audio detected.")
            raise ValueError(f"{self.episode_id}: No Audio detected.")
        return self._content

    def get_last_timestamp(self) -> Optional[str]:
        ts_pattern = r'\d+:\d+:\d+\.\d+|\d+:\d+\.\d+'
        matches = re.findall(ts_pattern, self.get_content())
        return matches[-1] if matches else None

    def timestamp_to_seconds(self, ts_str: Optional[str]) -> float:
        if not ts_str:
            return 0.0
        try:
            parts = ts_str.split(':')
            if len(parts) == 3:
                h, m, s = parts
                total = (int(h) * 3600) + (int(m) * 60) + float(s)
            elif len(parts) == 2:
                m, s = parts
                total = (int(m) * 60) + float(s)
            else:
                total = float(parts[0])
            return round(total, 2)
        except (ValueError, IndexError):
            return 0.0

    def get_video_duration(self) -> float:
        final_ts = self.get_last_timestamp()
        return self.timestamp_to_seconds(final_ts)

    def ensure_uploaded(self, model: GeminiModel, temp_path: str) -> str:
        """Uploads content via temporary file"""
        if self.file_id is None:
            logging.info(f"Uploading transcript to Gemini: {self.episode_id}")
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(self._content)
            uploaded_file = model.upload_file(temp_path)
            os.remove(temp_path)
            if not uploaded_file or not uploaded_file.name:
                raise ValueError(f"Failed to upload transcript: {self.episode_id}")
            self.file_id = uploaded_file.name
        if not self.file_id:
            raise ValueError("File ID not available after upload")
        return self.file_id