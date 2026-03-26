from brand_cli.fragments.base import Fragment

class TaggedExternalFragment(Fragment):
    def __init__(self, raw_content: str, start_tag: str, stop_tag: str = None):
        """
        :param raw_content: The string content already fetched by FileManager.
        :param start_tag: The marker to start extraction (e.g., "* **Saga I").
        :param stop_tag: Optional explicit marker to stop.
        """
        self.raw_content = raw_content
        self.start_tag = start_tag
        self.stop_tag = stop_tag

    def resolve(self) -> str:
        if not self.raw_content:
            return ""

        lines = self.raw_content.splitlines()
        extracted_lines = []
        is_capturing = False

        for line in lines:
            if self.start_tag in line:
                is_capturing = True
                continue 
            
            if is_capturing:
                # Stop if we hit the explicit stop tag or the next logical section
                if self.stop_tag and self.stop_tag in line:
                    break
                if not self.stop_tag and (line.startswith("* **") or line.startswith("##")):
                    break
                
                extracted_lines.append(line.strip())

        return "\n".join(extracted_lines).strip()