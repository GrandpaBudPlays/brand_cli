import json
import os
import pathlib

DEFAULT_CONFIG_PATH = pathlib.Path.cwd() / "brand_config.json"
CONTEXT_FILE_PATH = pathlib.Path.cwd() / ".brand_context"

DEFAULT_CONFIG = {
    "archive": {
        "content_root": "/home/bud/dev/Stream-Archive"
    },
    "ips": {
        "Valheim": {
            "terminology": {
                "ip": "Game",
                "series": "Chronicles",
                "season": "Saga",
                "arc": "Biome"
            },
            "series": {
                "Chronicles": {
                    "path_relative": "010-Valheim/Chronicles-Of-The-Exile",
                    "global_lexicon_path": "010-Valheim/Saga-Lexicon-Valheim.md",
                    "arc_metadata_file": "Biome.md",
                    "default_arcs": {}
                }
            }
        }
    },
    "reports": {
        "group_by_episode": True
    }
}

DEFAULT_CONTEXT = {
    "ip": None,
    "series": None,
    "season": None
}

def load_config():
    config_path_str = os.getenv("BRAND_CONFIG_PATH")
    if config_path_str:
        config_path = pathlib.Path(config_path_str)
    else:
        config_path = DEFAULT_CONFIG_PATH
        if not config_path.exists():
            script_dir = pathlib.Path(__file__).parent
            config_path = script_dir / "brand_config.json"

    if not config_path.exists():
        print(f"Creating default config at {config_path}")
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
            return DEFAULT_CONFIG
        except Exception as e:
            print(f"Error creating default config: {e}. Using in-memory default.")
            return DEFAULT_CONFIG

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            user_config = json.load(f)

        merged_config = DEFAULT_CONFIG.copy()
        for key in ["archive", "ips", "reports"]:
            if key in user_config:
                merged_config[key] = user_config[key]
        return merged_config

    except Exception as e:
        print(f"Error reading config at {config_path}: {e}")
        return DEFAULT_CONFIG

def load_context():
    if not CONTEXT_FILE_PATH.exists():
        return DEFAULT_CONTEXT.copy()
    try:
        with open(CONTEXT_FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return DEFAULT_CONTEXT.copy()

def save_context(context_data):
    try:
        with open(CONTEXT_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(context_data, f, indent=4)
        print(f"Successfully saved context to {CONTEXT_FILE_PATH}")
    except Exception as e:
        print(f"Error saving context: {e}")

# Global instances
CONFIG = load_config()
CONTEXT = load_context()
