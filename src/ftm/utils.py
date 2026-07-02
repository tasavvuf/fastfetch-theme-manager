import subprocess
import json
import os
from typing import List, Optional, Dict, Any
from pathlib import Path


def run_command(cmd: List[str], verbose=False) -> bool:
    try:
        result = subprocess.run(
            cmd,
            stdout=None if verbose else subprocess.PIPE,
            stderr=None if verbose else subprocess.PIPE,
        )
        if result.returncode != 0 and verbose:
            try:
                print(result.stderr.decode(), end="")
            except (UnicodeDecodeError, AttributeError):
                pass
        return result.returncode == 0
    except FileNotFoundError:
        return False


def run_command_output(cmd: List[str]) -> str:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return result.stdout.strip()
        return ""
    except Exception:
        return ""


def read_jsonc(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        text = path.read_text()
        return json.loads(text)
    except (json.JSONDecodeError, OSError):
        return None


def write_jsonc(path: Path, data: Dict[str, Any]):
    text = json.dumps(data, indent=4)
    if path.suffix == ".jsonc":
        text = "// Fastfetch Theme Manager generated config\n" + text
    path.write_text(text)
