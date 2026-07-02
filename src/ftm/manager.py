import shutil
import sys
import time
import os
from pathlib import Path
from typing import List

from ftm.config import CONFIG_DIR, CONFIG_FILE, BACKUP_DIR, ensure_dirs
from ftm.style import Style
from ftm.themes import resolve_theme, ThemeEntry
from ftm.utils import run_command
from ftm.fastfetch_version import FastfetchCompat


def backup_config():
    if CONFIG_FILE.exists():
        timestamp = int(time.time())
        backup_path = BACKUP_DIR / f"config_{timestamp}.jsonc"
        try:
            shutil.copy2(CONFIG_FILE, backup_path)
            backups = sorted(BACKUP_DIR.glob("config_*.jsonc"), key=os.path.getmtime)
            while len(backups) > 10:
                backups.pop(0).unlink()
            return True
        except Exception:
            pass
    return False


def list_backups() -> List[Path]:
    return sorted(BACKUP_DIR.glob("config_*.jsonc"), key=os.path.getmtime, reverse=True)


def restore_backup():
    backups = list_backups()
    if not backups:
        Style.error("No backups found to restore.")
        return
    latest = backups[0]
    try:
        shutil.copy2(latest, CONFIG_FILE)
        Style.success(f"Restored configuration from {latest.name}")
    except Exception as e:
        Style.error(f"Failed to restore backup: {e}")


def apply_theme(path_str: str, no_backup: bool = False):
    target = Path(path_str)
    if not target.exists():
        entry = resolve_theme(path_str)
        if entry and entry.path:
            target = entry.path
        else:
            Style.error(f"Theme not found: {path_str}")
            return
    ensure_dirs()
    if not no_backup:
        backup_config()
    try:
        shutil.copy2(target, CONFIG_FILE)
        Style.success(f"Applied theme: {target.name}")
        print(f"{Style.DIM}Validating...{Style.RESET}")
        if not run_command(["fastfetch", "--config", str(CONFIG_FILE)], verbose=False):
            Style.warning("Theme applied, but fastfetch reported errors/warnings.")
            if sys.stdin.isatty() and input("Revert to previous? [y/N] ").lower() == 'y':
                restore_backup()
        else:
            run_command(["fastfetch"], verbose=True)
    except Exception as e:
        Style.error(f"Critical error applying theme: {e}")
        if not no_backup:
            restore_backup()


def reset_to_defaults(force: bool = False):
    if not force:
        if input(f"{Style.RED}WARNING: This will reset your fastfetch config. Continue? [y/N] {Style.RESET}").lower() != 'y':
            return
    backup_config()
    compat = FastfetchCompat()
    if compat.supports("gen_config_force"):
        if run_command(["fastfetch", "--gen-config-force"]):
            Style.success("Reset complete. Default config generated.")
            run_command(["fastfetch"])
        else:
            Style.error("Failed to generate default config.")
    else:
        Style.error("This fastfetch version does not support --gen-config-force")
