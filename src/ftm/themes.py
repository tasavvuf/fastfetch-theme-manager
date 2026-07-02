from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any
import subprocess

from ftm.config import USER_THEMES_DIR, CONFIG_FILE
from ftm.utils import read_jsonc


@dataclass
class ThemeEntry:
    key: str
    origin: str
    path: Optional[Path]


def get_fastfetch_presets() -> List[Path]:
    try:
        proc = subprocess.run(
            ["fastfetch", "--list-data-paths"],
            capture_output=True, text=True, timeout=5
        )
        if proc.returncode == 0:
            paths = [Path(p.strip()) for p in proc.stdout.splitlines() if p.strip()]
            valid = []
            for p in paths:
                if (p / "presets").exists():
                    valid.append(p / "presets")
                if (p / "fastfetch/presets").exists():
                    valid.append(p / "fastfetch/presets")
            if valid:
                return valid
    except Exception:
        pass
    candidates = [
        Path("/usr/share/fastfetch/presets"),
        Path("/usr/share/fastfetch/fastfetch/presets"),
        Path("/usr/local/share/fastfetch/presets"),
        Path.home() / ".local/share/fastfetch/presets",
    ]
    return [p for p in candidates if p.exists()]


def list_themes() -> List[ThemeEntry]:
    entries = []
    preset_dirs = get_fastfetch_presets()
    for d in preset_dirs:
        for f in sorted(d.glob("*.jsonc")):
            entries.append(ThemeEntry(f.stem, "System", f))
        example_dir = d / "examples"
        if example_dir.exists():
            for f in sorted(example_dir.glob("*.jsonc")):
                entries.append(ThemeEntry(f"examples/{f.stem}", "Example", f))
    if USER_THEMES_DIR.exists():
        for f in sorted(USER_THEMES_DIR.glob("*.jsonc")):
            entries.append(ThemeEntry(f"user/{f.stem}", "User", f))
    unique = {}
    for e in entries:
        if e.key not in unique:
            unique[e.key] = e
    return sorted(unique.values(), key=lambda x: x.key)


def resolve_theme(name: str) -> Optional[ThemeEntry]:
    themes = list_themes()
    for t in themes:
        if t.key == name:
            return t
    for t in themes:
        if t.key.endswith(f"/{name}"):
            return t
    for t in themes:
        if name.lower() in t.key.lower():
            return t
    return None


def get_theme_modules(path: Path) -> Optional[List[str]]:
    data = read_jsonc(path)
    if data is None:
        return None
    modules = data.get("modules")
    if not isinstance(modules, list):
        return None
    result = []
    for m in modules:
        if isinstance(m, str):
            result.append(m)
        elif isinstance(m, dict) and "type" in m:
            result.append(m["type"])
    return result if result else None
