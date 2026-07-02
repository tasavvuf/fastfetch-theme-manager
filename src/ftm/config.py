from pathlib import Path
import os
import sys

APP_NAME = "Fastfetch Theme Manager"
VERSION = "3.0.0"

CONFIG_DIR = Path.home() / ".config/fastfetch"
CONFIG_FILE = CONFIG_DIR / "config.jsonc"
USER_THEMES_DIR = Path.home() / ".local/share/fastfetch/themes"
BACKUP_DIR = Path.home() / ".local/share/fastfetch/backups"
FTM_CONFIG_DIR = Path.home() / ".config/fastfetch-theme-manager"
FTM_CONFIG_FILE = FTM_CONFIG_DIR / "config.json"


def ensure_dirs():
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        USER_THEMES_DIR.mkdir(parents=True, exist_ok=True)
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        FTM_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"Error creating directories: {e}")
        sys.exit(1)


def load_ftm_config() -> dict:
    ensure_dirs()
    if FTM_CONFIG_FILE.exists():
        try:
            import json
            with open(FTM_CONFIG_FILE) as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_ftm_config(data: dict):
    import json
    ensure_dirs()
    with open(FTM_CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)
