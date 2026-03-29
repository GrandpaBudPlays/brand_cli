import yaml
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

class PromptLoader:
    def __init__(self, prompts_dir="src/brand_cli/resources/prompts"):
        self.prompts_dir = Path(prompts_dir)
        self.env = Environment(
            loader=FileSystemLoader(self.prompts_dir),
            autoescape=True
        )

    def load_prompt(self, operation_name, fragments=None, session_data=None):
        fragments = fragments or {}
        session_data = session_data or {}
        
        try:
            # Try game-specific prompt first if game context exists
            if session_data.get("game"):
                game_file = self.prompts_dir / "games" / f"{session_data['game']}.yaml"
                if game_file.exists():
                    with open(game_file) as f:
                        prompt_data = yaml.safe_load(f)
                        return self._render_prompt(prompt_data, fragments, session_data)
            
            # Fall back to operation prompt
            op_file = self.prompts_dir / f"{operation_name}.yaml"
            with open(op_file) as f:
                prompt_data = yaml.safe_load(f)
                return self._render_prompt(prompt_data, fragments, session_data)
                
        except FileNotFoundError:
            raise ValueError(f"Prompt file not found for {operation_name}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in prompt file: {str(e)}")

    def load_config(self, name):
        """Loads a raw YAML file from the prompts directory."""
        path = self.prompts_dir / f"{name}.yaml"
        try:
            with open(path) as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise ValueError(f"Config file not found: {name}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in config file: {str(e)}")

    def _render_prompt(self, prompt_data, fragments, session_data):
        context = {
            "fragments": fragments,
            "session": session_data
        }
        
        return {
            "system_prompt": self.env.from_string(prompt_data["system_prompt"]).render(context),
            "user_prompt": self.env.from_string(prompt_data["user_prompt"]).render(context)
        }