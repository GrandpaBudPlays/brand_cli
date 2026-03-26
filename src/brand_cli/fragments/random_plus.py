from typing import Optional
from brand_cli.fragments.base import Fragment
import random
import re

class RandPlus(Fragment):
    def __init__(self, raw_content: str, start_tag: str = "-Begin Random-"):
        super().__init__()
        self.raw_content = raw_content
        self.start_tag = start_tag

    def resolve(self) -> str:
        if not self.raw_content:
            return ""

        # 1. Determine the range for the random selection
        matches = re.findall(r'^\s*(\d+)\.', self.raw_content, re.MULTILINE)
        if not matches:
            return self.raw_content # If no list found, just return the whole thing
        
        highest_num = max(int(n) for n in matches)
        selected_id = random.randint(1, highest_num)
        target_prefix = f"{selected_id}."

        lines = self.raw_content.splitlines()
        output_lines = []
        is_searching_for_cta = False
        
        for line in lines:
            clean_line = line.strip()
            
            # Phase 1: Keep everything before the tag
            if self.start_tag in clean_line:
                is_searching_for_cta = True
                continue 
            
            if not is_searching_for_cta:
                # Still in the "Intro" section of the file
                output_lines.append(line)
            else:
                # Phase 2: We are past the tag, look for the specific number
                if clean_line.startswith(target_prefix):
                    # Extract text after "X. "
                    cta_text = clean_line[len(target_prefix):].strip()
                    output_lines.append(cta_text)
                    # We found our random pick, we can stop entirely
                    break

        return "\n".join(output_lines).strip()