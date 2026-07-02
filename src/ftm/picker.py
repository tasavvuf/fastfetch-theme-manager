import shutil
import subprocess
import os
import sys
import tempfile
from pathlib import Path
from ftm.themes import list_themes, get_theme_modules, ThemeEntry
from ftm.style import Style
from ftm.manager import apply_theme
from ftm.utils import read_jsonc


def _build_preview(path_str: str) -> str:
    """Build shell command for fzf preview showing theme info + fastfetch output."""
    if not path_str or path_str == "None" or not Path(path_str).exists():
        return "echo '(preview unavailable)'"

    parts = []
    try:
        data = read_jsonc(Path(path_str))
        if data:
            mods = data.get("modules", [])
            mod_keys = [m if isinstance(m, str) else m.get("type", "?") for m in mods] if isinstance(mods, list) else []

            logo = data.get("logo", {})
            lt = logo.get("type", "auto") if isinstance(logo, dict) else "auto"
            parts.append(f"echo 'Logo: {lt}'")

            display = data.get("display", {})
            if isinstance(display, dict):
                sep = display.get("separator", "")
                if sep:
                    col = display.get("color", "blue")
                    parts.append(f"echo 'Sep: \"{sep}\" | Color: {col}'")

            if mod_keys:
                parts.append(f"echo 'Modules ({len(mod_keys)}): {' '.join(mod_keys)}'")
            parts.append("echo '---'")
            parts.append("echo 'Fastfetch output:'")

            if mod_keys:
                structure = ":".join(mod_keys[:20])
                parts.append(f"fastfetch --config {path_str} --structure {structure} 2>/dev/null")
            else:
                parts.append(f"fastfetch --config {path_str} 2>/dev/null")

            return " && ".join(parts)
    except Exception:
        pass

    return f"echo 'Fastfetch output:' && fastfetch --config {path_str} 2>/dev/null || echo '(preview unavailable)'"


def run_fzf_picker():
    if not shutil.which("fzf"):
        Style.error("fzf is not installed. Install it with your package manager.")
        return

    if not sys.stdin.isatty():
        Style.error("Interactive picker requires a terminal. Run 'ftm pick' in an interactive shell.")
        return

    themes = list_themes()
    if not themes:
        Style.error("No themes found. Use 'ftm build' or 'ftm pull' to get some.")
        return

    input_lines = []
    for t in themes:
        if not t.path or not t.path.exists():
            continue
        mods = get_theme_modules(t.path)
        count = len(mods) if mods else 0
        size = t.path.stat().st_size
        size_str = f"{size // 1024}k" if size > 1024 else f"{size}b"
        input_lines.append(f"{t.key}\t{t.origin}\t{count}m\t{size_str}\t{t.path}")

    if not input_lines:
        Style.error("No valid themes found.")
        return

    input_str = "\n".join(input_lines)

    tmp = tempfile.NamedTemporaryFile(mode="w", delete=False)
    try:
        tmp.write(input_str)
        tmp.close()

        # fzf column placeholders: {1}=key, {2}=origin, {3}=modules, {4}=size, {5}=path
        preview = (
            'cat={} && '
            'echo "Theme: {1} ({2})" && '
            'echo "Modules: {3}  |  Size: {4}" && '
            'echo --- && '
            'fastfetch --config {5} 2>/dev/null || '
            'echo "(preview unavailable)"'
        )

        fzf_cmd = [
            "fzf",
            "--delimiter=\t",
            "--with-nth=1,2,3,4",
            "--preview", preview,
            "--preview-window=right,65%,border-left,wrap",
            "--header", "^M Apply  |  ^C Quit",
        ]

        with open(tmp.name) as f:
            proc = subprocess.Popen(
                fzf_cmd,
                stdin=f,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = proc.communicate()

        if stdout and stdout.strip():
            selected = stdout.decode().strip().split("\t")[0]
            Style.info(f"Applying: {selected}")
            apply_theme(selected)
    except KeyboardInterrupt:
        print()
    except Exception as e:
        Style.error(f"Picker error: {e}")
    finally:
        os.unlink(tmp.name)
