import json
import os
import pathlib

DEFAULT_CONFIG_PATH = pathlib.Path.cwd() / "brand_config.json"

DEFAULT_CONFIG = {
    "archive": {
        "valheim_root": "010-Valheim/Chronicles-Of-The-Exile",
        "lexicon_path": "010-Valheim/Saga-Lexicon-Valheim.md"
    },
    "brand": {
        "default_biomes": {
            "Saga I": "Meadows",
            "Saga II": "Black Forest",
            "Saga III": "Swamp",
            "Saga IV": "Mountains",
            "Saga V": "Plains",
            "Saga VI": "Ashlands"
        }
    },
    "reports": {
        "group_by_episode": True
    }
}

def load_config():
    config_path_str = os.getenv("BRAND_CONFIG_PATH")
    if config_path_str:
        config_path = pathlib.Path(config_path_str)
    else:
        # Check current working directory
        config_path = pathlib.Path.cwd() / "brand_config.json"
        if not config_path.exists():
            # Fallback to the Scripts directory if not found in cwd
            script_dir = pathlib.Path(__file__).parent
            config_path = script_dir / "brand_config.json"

    if not config_path.exists():
        print(f"Warning: brand_config.json not found at {config_path}. Using default configuration.")
        return DEFAULT_CONFIG

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            user_config = json.load(f)

        # Basic deep merge for the 3 main keys
        merged_config = DEFAULT_CONFIG.copy()
        for key in ["archive", "brand", "reports"]:
            if key in user_config:
                merged_config[key].update(user_config[key])
        return merged_config

    except Exception as e:
        print(f"Error reading config at {config_path}: {e}")
        return DEFAULT_CONFIG

# Global config instance loaded once
CONFIG = load_config()
