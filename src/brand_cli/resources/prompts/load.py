import yaml
from pathlib import Path

def load_prompt(name: str) -> dict:
    """Load prompt from YAML file in resources/prompts."""
    path = Path(__file__).parent / f"{name}.yaml"
    with open(path) as f:
        return yaml.safe_load(f)