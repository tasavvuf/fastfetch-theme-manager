import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from ftm.config import USER_THEMES_DIR, ensure_dirs
from ftm.style import Style
from ftm.fastfetch_version import FastfetchCompat
from ftm.moduledb import get_modules, get_available_sub_options, ModuleDef
from ftm.manager import apply_theme
from ftm.utils import read_jsonc, write_jsonc, run_command
from itertools import cycle


def ask_choice(prompt: str, options: List[str], default: int = 1) -> str:
    print(f"\n{Style.BOLD}? {prompt}{Style.RESET}")
    for i, opt in enumerate(options):
        marker = " [default]" if i + 1 == default else ""
        print(f"  {Style.CYAN}{i+1}){Style.RESET} {opt}{Style.DIM}{marker}{Style.RESET}")
    while True:
        try:
            choice = input(f"{Style.DIM}Select [1-{len(options)}]: {Style.RESET}")
            if not choice.strip():
                return options[default - 1]
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    return options[idx]
        except KeyboardInterrupt:
            print()
            sys.exit(0)


def ask_yesno(prompt: str, default: bool = True) -> bool:
    suffix = " [Y/n]" if default else " [y/N]"
    try:
        answer = input(f"{Style.BOLD}? {prompt}{Style.DIM}{suffix}: {Style.RESET}").strip().lower()
        if not answer:
            return default
        return answer.startswith("y")
    except KeyboardInterrupt:
        print()
        sys.exit(0)


def ask_string(prompt: str, default: str = "") -> str:
    try:
        dfl = f" [{default}]" if default else ""
        val = input(f"{Style.BOLD}? {prompt}{Style.DIM}{dfl}: {Style.RESET}").strip()
        return val if val else default
    except KeyboardInterrupt:
        print()
        sys.exit(0)


def show_current_config(config: Dict[str, Any]):
    print(f"\n{Style.DIM}{'─' * 50}{Style.RESET}")
    print(f"{Style.CYAN}Current Theme Preview:{Style.RESET}")
    logo = config.get("logo", {})
    if isinstance(logo, dict):
        lt = logo.get("type", "auto")
        print(f"  Logo: {lt}")
        if "source" in logo:
            print(f"  Logo source: {logo['source']}")
    display = config.get("display", {})
    if isinstance(display, dict):
        print(f"  Separator: '{display.get('separator', '')}'")
        print(f"  Color: {display.get('color', 'blue')}")
        if display.get("keyWidth"):
            print(f"  Key width: {display['keyWidth']}")
        if display.get("key", {}).get("type"):
            print(f"  Key type: {display['key']['type']}")
    mods = config.get("modules", [])
    if mods:
        print(f"  Modules ({len(mods)}):")
        for i, m in enumerate(mods):
            if isinstance(m, str):
                print(f"    {i+1}. {m}")
            elif isinstance(m, dict):
                extra = ", ".join(f"{k}={v}" for k, v in m.items() if k != "type")
                print(f"    {i+1}. {m.get('type', '?')} ({extra})")
    print(f"{Style.DIM}{'─' * 50}{Style.RESET}\n")


def build_theme(start_from: Optional[Dict[str, Any]] = None, name_hint: str = ""):
    Style.print_header("Theme Builder")
    compat = FastfetchCompat()
    ver_str = compat.version_str()
    print(f"{Style.DIM}fastfetch {ver_str} — {compat.version_str()} compatible modules{Style.RESET}")
    available_modules = get_modules(compat)

    config: Dict[str, Any] = start_from or {
        "$schema": "https://github.com/fastfetch-cli/fastfetch/raw/dev/doc/json_schema.json",
        "logo": {"type": "auto"},
        "display": {
            "separator": " \u279c  ",
            "color": "blue",
        },
        "modules": []
    }

    if compat.supports("display_disable_linewrap"):
        config.setdefault("display", {})["disableLinewrap"] = False

    if not start_from:
        logo_type = ask_choice("Select Logo Style", [
            "Current OS (Auto)", "Small/Minimal", "None (Text Only)",
            "Built-in ASCII", "Image file (Kitty)", "Image file (Sixel)", "Image file (iTerm)", "Custom Image Path"
        ], default=1)
        logo_map = {
            "Current OS (Auto)": {"type": "auto"},
            "Small/Minimal": {"type": "small"},
            "None (Text Only)": {"type": "none"},
            "Built-in ASCII": {"type": "builtin"},
            "Image file (Kitty)": {"type": "kitty", "source": ""},
            "Image file (Sixel)": {"type": "sixel", "source": ""},
            "Image file (iTerm)": {"type": "iterm", "source": ""},
            "Custom Image Path": {"type": "", "source": ""},
        }
        config["logo"] = logo_map[logo_type].copy()
        if logo_type == "Custom Image Path":
            config["logo"]["type"] = ask_string("Logo type (auto/builtin/small/kitty/sixel/iterm)", "auto")
            config["logo"]["source"] = ask_string("Image file path")
        elif "source" in config["logo"]:
            config["logo"]["source"] = ask_string("Image file path")

    if not start_from:
        border = ask_choice("Select Border Style", ["None (arrow)", "Double", "Rounded", "Solid", "Custom"])
        sep_map = {
            "None (arrow)": " \u279c  ",
            "Double": " \u2551 ",
            "Rounded": " \u2502 ",
            "Solid": " \u2503 ",
            "Custom": "",
        }
        sep = sep_map[border]
        if border == "Custom":
            sep = ask_string("Enter separator string", " | ")
        config["display"]["separator"] = sep

        color = ask_choice("Select Primary Color", ["Default", "Blue", "Red", "Green", "Magenta", "Yellow", "Cyan", "White", "Custom"])
        config["display"]["color"] = color.lower() if color != "Default" and color != "Custom" else "blue"
        if color == "Custom":
            config["display"]["color"] = ask_string("Enter color name (e.g. cyan, #ff0000, @34)")

    if ask_yesno("Configure display options?", default=False):
        display = config.setdefault("display", {})
        if ask_yesno("Use icon-style keys?", default=False):
            display["key"] = display.get("key", {})
            display["key"]["type"] = "icon"
        key_width = ask_string("Key width (number, or empty for auto)")
        if key_width.isdigit():
            display["keyWidth"] = int(key_width)
        if ask_yesno("Hide module keys?", default=False):
            display.setdefault("key", {})["type"] = "none"

    print(f"\n{Style.BOLD}Select Modules to Display{Style.RESET}")
    print(f"{Style.DIM}Available: {len(available_modules)} modules (fastfetch {ver_str}){Style.RESET}")

    preset_choice = ask_choice("Choose preset or custom", [
        "Standard (Recommended)", "Minimal (Essential)", "All Info",
        "Developer Focus", "Gaming Focus", "System Admin", "Custom..."
    ], default=1)

    preset_map = {
        "Standard (Recommended)": ["title", "separator", "os", "host", "kernel",
                                     "uptime", "packages", "shell", "de", "terminal",
                                     "cpu", "memory", "break", "colors"],
        "Minimal (Essential)": ["os", "kernel", "packages", "memory"],
        "All Info": [m.key for m in available_modules],
        "Developer Focus": ["title", "separator", "os", "kernel", "uptime",
                             "shell", "terminal", "editor", "cpu", "memory",
                             "disk", "break", "colors"],
        "Gaming Focus": ["title", "separator", "os", "host", "kernel",
                          "gpu", "cpu", "memory", "disk", "break", "colors"],
        "System Admin": ["title", "separator", "os", "host", "uptime",
                          "kernel", "packages", "cpu", "memory", "disk",
                          "swap", "processes", "localip", "break", "colors"],
    }

    selected = []
    if preset_choice == "Custom...":
        print("Select each module individually:")
        all_mods = list(available_modules)
        for i, mod in enumerate(all_mods):
            include = ask_yesno(f"  [{i+1}/{len(all_mods)}] {mod.label}?", default=False)
            if include:
                selected.append(mod)
        if not selected:
            Style.warning("No modules selected. Adding standard set.")
            preset_choice = "Standard (Recommended)"
            selected = [m for m in available_modules if m.key in preset_map["Standard (Recommended)"]]
    else:
        keys = preset_map[preset_choice]
        selected = [m for m in available_modules if m.key in keys]

    if preset_choice != "Custom..." and ask_yesno("Customize module selection?", default=False):
        print("Toggle modules (y=include, n=exclude):")
        all_mods = list(available_modules)
        for mod in all_mods:
            currently_in = mod in selected
            if currently_in:
                if not ask_yesno(f"  Keep {mod.label}?", default=True):
                    selected.remove(mod)
            else:
                if ask_yesno(f"  Add {mod.label}?", default=False):
                    selected.append(mod)

    reorder = ask_yesno("Reorder modules?", default=False)
    if reorder:
        print("Reorder modules (drag-and-drop style):")
        print("Enter new order as comma-separated numbers (1 = first):")
        for i, m in enumerate(selected):
            print(f"  {i+1}. {Style.CYAN}{m.key}{Style.RESET} — {m.label}")
        try:
            order = input(f"{Style.BOLD}New order (e.g. 1,3,2,4): {Style.RESET}").strip()
            if order:
                indices = [int(x.strip()) - 1 for x in order.split(",") if x.strip().isdigit()]
                indices = [i for i in indices if 0 <= i < len(selected)]
                if len(indices) == len(selected):
                    selected = [selected[i] for i in indices]
                    Style.success("Modules reordered.")
        except (ValueError, IndexError):
            Style.warning("Invalid order, keeping current.")

    config["modules"] = []
    for mod in selected:
        entry = _configure_module(mod, compat)
        if entry is not None:
            config["modules"].append(entry)

    show_current_config(config)

    if ask_yesno("Add a command module?", default=False):
        cmd_type = ask_choice("Command output source", ["Shell command", "Custom text"])
        cmd_mod = {"type": "command"}
        if cmd_type == "Shell command":
            cmd_mod["text"] = ask_string("Shell command to run")
        else:
            cmd_mod["format"] = ask_string("Custom text to display")
        if compat.supports("command_split_lines") and ask_yesno("Split output into lines?", default=False):
            cmd_mod["splitLines"] = True
        config["modules"].append(cmd_mod)

    if ask_yesno("Save theme?", default=True):
        name = ask_string("Theme name", name_hint or "my_theme")
        if not name:
            name = "my_theme"
        if not name.endswith(".jsonc"):
            name += ".jsonc"
        ensure_dirs()
        out_path = USER_THEMES_DIR / name
        try:
            text = json.dumps(config, indent=4)
            out_path.write_text(f"// {Style.RESET}Fastfetch Theme Manager v3\n" + text)
            Style.success(f"Saved to {out_path}")
            if ask_yesno("Apply now?", default=True):
                apply_theme(str(out_path))
        except Exception as e:
            Style.error(f"Save failed: {e}")


def _configure_module(mod: ModuleDef, compat: FastfetchCompat):
    entry: Dict[str, Any] = {"type": mod.key}
    sub_opts = get_available_sub_options(mod.key, compat)
    has_sub_config = sub_opts and any(
        True for _ in sub_opts
    )
    if has_sub_config:
        if ask_yesno(f"Configure {mod.label} options?", default=False):
            for opt in sub_opts:
                if opt.type == "bool":
                    if ask_yesno(f"  {opt.label}?", default=opt.default):
                        entry[opt.jsonschema_key or opt.key] = True
                elif opt.type == "str":
                    val = ask_string(opt.label)
                    if val:
                        entry[opt.jsonschema_key or opt.key] = val
            if ask_yesno("  Custom format string?", default=False):
                fmt = ask_string("Format (e.g. {name} @ {version})")
                if fmt:
                    entry["format"] = fmt
            if ask_yesno("  Custom output color?", default=False):
                oc = ask_string("Output color name")
                if oc:
                    entry["outputColor"] = oc
            if ask_yesno("  Custom key color?", default=False):
                kc = ask_string("Key color name")
                if kc:
                    entry["keyColor"] = kc
            if len(entry) > 1:
                return entry
            return mod.key
        return mod.key
    if ask_yesno(f"Add {mod.label}?", default=True):
        return mod.key
    return None


def edit_theme(entry):
    data = read_jsonc(entry.path)
    if not data:
        Style.error(f"Could not read theme: {entry.path}")
        return
    Style.print_header(f"Editing: {entry.key}")
    print(f"{Style.DIM}Loaded from {entry.path}{Style.RESET}")
    show_current_config(data)
    keep_build = ask_yesno("Rebuild this theme with the wizard?", default=True)
    if not keep_build:
        return
    name_hint = entry.key.split("/")[-1] if "/" in entry.key else entry.key
    build_theme(start_from=data, name_hint=name_hint)
