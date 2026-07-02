import argparse
import sys
import json
import shutil
import time
from pathlib import Path

from ftm import APP_NAME, VERSION
from ftm.config import ensure_dirs, CONFIG_DIR, CONFIG_FILE, USER_THEMES_DIR, BACKUP_DIR
from ftm.style import Style
from ftm.detection import detect_package_managers, detect_distro, suggest_install
from ftm.fastfetch_version import detect_fastfetch_version, FastfetchCompat
from ftm.themes import list_themes, resolve_theme, get_theme_modules
from ftm.manager import apply_theme, reset_to_defaults, backup_config, restore_backup, list_backups
from ftm.picker import run_fzf_picker
from ftm.builder import build_theme, edit_theme
from ftm.utils import run_command, read_jsonc, write_jsonc

import urllib.request
import urllib.error


def cmd_info():
    Style.print_header(f"{APP_NAME} v{VERSION}")
    version = detect_fastfetch_version()
    distro = detect_distro()
    pkg_managers = detect_package_managers()
    compat = FastfetchCompat()
    themes = list_themes()
    user_count = sum(1 for t in themes if t.origin == "User")
    print(f"{Style.BOLD}fastfetch version:{Style.RESET}  {version or Style.RED + 'not found' + Style.RESET}")
    print(f"{Style.BOLD}Compatible up to:{Style.RESET} {compat.version_str()}")
    print(f"{Style.BOLD}Distribution:{Style.RESET}     {distro.pretty_name or distro.id or 'unknown'} {distro.version_id}")
    print(f"{Style.BOLD}Package Managers:{Style.RESET} {', '.join(pkg_managers[:8]) if pkg_managers else 'none'}" + (f" +{len(pkg_managers)-8}" if len(pkg_managers) > 8 else ""))
    print(f"{Style.BOLD}Config dir:{Style.RESET}       {CONFIG_DIR}")
    print(f"{Style.BOLD}Current config:{Style.RESET}   {'exists' if CONFIG_FILE.exists() else Style.DIM + 'not set' + Style.RESET}")
    print(f"{Style.BOLD}User themes:{Style.RESET}      {user_count} installed, {len(themes)} total")
    print(f"{Style.BOLD}Backups:{Style.RESET}          {len(list_backups())} available")


def cmd_list(args):
    themes = list_themes()
    if not themes:
        Style.info("No themes found. Use 'ftm build' or 'ftm pull' to get some.")
        return
    origin_filter = getattr(args, 'origin', None)
    query_filter = getattr(args, 'query', None)
    if origin_filter:
        themes = [t for t in themes if t.origin.lower() == origin_filter.lower()]
    if query_filter:
        q = query_filter.lower()
        themes = [t for t in themes if q in t.key.lower()]
    if not themes:
        Style.info("No matching themes.")
        return
    col_key = "KEY"
    col_src = "SOURCE"
    col_mods = "MODULES"
    col_size = "SIZE"
    col_time = "MODIFIED"
    print(f"\n{Style.BOLD}{col_key:<40} {col_src:<8} {col_mods:<8} {col_size:<8} {col_time}{Style.RESET}")
    print("-" * 110)
    for t in themes:
        c = Style.GREEN if t.origin == "User" else (Style.YELLOW if t.origin == "Example" else Style.BLUE)
        mods = get_theme_modules(t.path)
        mod_count = len(mods) if mods else 0
        size = t.path.stat().st_size if t.path and t.path.exists() else 0
        size_str = f"{size // 1024}KB" if size > 1024 else f"{size}B"
        try:
            mtime = time.strftime("%b%d %H:%M", time.localtime(t.path.stat().st_mtime))
        except Exception:
            mtime = ""
        print(f"{t.key:<40} {c}{t.origin:<8}{Style.RESET} {mod_count:<8} {size_str:<8} {mtime}")
    print()
    sys_count = sum(1 for t in themes if t.origin == "System")
    ex_count = sum(1 for t in themes if t.origin == "Example")
    us_count = sum(1 for t in themes if t.origin == "User")
    print(f"{Style.DIM}Total: {len(themes)} ({us_count} user, {sys_count} system, {ex_count} examples){Style.RESET}\n")


def cmd_describe(args):
    entry = resolve_theme(args.theme)
    if not entry or not entry.path:
        Style.error(f"Theme not found: {args.theme}")
        return
    t = entry
    print(f"\n{Style.BOLD}{Style.GREEN}{t.key}{Style.RESET}")
    print(f"{Style.DIM}{'=' * len(t.key)}{Style.RESET}")
    print(f"{Style.BOLD}Origin:{Style.RESET}     {t.origin}")
    print(f"{Style.BOLD}File:{Style.RESET}       {t.path}")
    size = t.path.stat().st_size
    print(f"{Style.BOLD}Size:{Style.RESET}       {size // 1024}KB ({size} bytes)")
    try:
        mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t.path.stat().st_mtime))
        print(f"{Style.BOLD}Modified:{Style.RESET}   {mtime}")
    except Exception:
        pass
    data = read_jsonc(t.path)
    if data:
        mods = data.get("modules", [])
        mod_keys = []
        for m in mods:
            if isinstance(m, str):
                mod_keys.append(m)
            elif isinstance(m, dict):
                mod_keys.append(m.get("type", "?"))
        print(f"{Style.BOLD}Modules ({len(mod_keys)}):{Style.RESET} ", end="")
        cols = [Style.GREEN if k in ("title", "os", "colors") else
                Style.CYAN if k in ("separator", "break") else
                Style.YELLOW if k in ("gpu", "cpu", "memory", "disk") else
                Style.RESET for k in mod_keys]
        for i, k in enumerate(mod_keys):
            print(f"{cols[i]}{k}{Style.RESET}", end="")
            if i < len(mod_keys) - 1:
                print(", ", end="")
        print()
        logo = data.get("logo", {})
        if isinstance(logo, dict):
            lt = logo.get("type", "auto")
            print(f"{Style.BOLD}Logo:{Style.RESET}       {lt}")
        display = data.get("display", {})
        if isinstance(display, dict):
            sep = display.get("separator", "")
            if sep:
                print(f"{Style.BOLD}Separator:{Style.RESET}   '{sep}'")
            col = display.get("color", "default")
            print(f"{Style.BOLD}Color:{Style.RESET}       {col}")
    print()


def cmd_search(args):
    cmd_list(args)


def cmd_set(args):
    apply_theme(args.theme, no_backup=args.no_backup)


def cmd_preview(args):
    entry = resolve_theme(args.theme)
    if not entry or not entry.path:
        Style.error(f"Theme not found: {args.theme}")
        return
    Style.info(f"Previewing: {entry.key} ({entry.origin})")
    mods = get_theme_modules(entry.path)
    if mods:
        structure = ":".join(mods)
        run_command(["fastfetch", "--config", str(entry.path), "--structure", structure])
    else:
        run_command(["fastfetch", "--config", str(entry.path)])


def cmd_pick():
    run_fzf_picker()


def cmd_build():
    build_theme()


def cmd_edit(args):
    entry = resolve_theme(args.theme)
    if not entry or not entry.path:
        Style.error(f"Theme not found: {args.theme}")
        return
    edit_theme(entry)


def cmd_export(args):
    entry = resolve_theme(args.theme)
    if not entry or not entry.path:
        Style.error(f"Theme not found: {args.theme}")
        return
    if args.output:
        dest = Path(args.output)
    else:
        dest = Path.cwd() / f"{entry.key.replace('/', '_')}.jsonc"
    try:
        shutil.copy2(entry.path, dest)
        Style.success(f"Exported to {dest}")
    except Exception as e:
        Style.error(f"Export failed: {e}")


def cmd_import(args):
    src = Path(args.file)
    if not src.exists():
        Style.error(f"File not found: {args.file}")
        return
    ensure_dirs()
    dest = USER_THEMES_DIR / src.name
    try:
        shutil.copy2(src, dest)
        Style.success(f"Imported {src.name} to user themes")
        if args.apply:
            apply_theme(str(dest))
        elif sys.stdin.isatty():
            if input("Apply now? [y/N] ").lower() == 'y':
                apply_theme(str(dest))
    except Exception as e:
        Style.error(f"Import failed: {e}")


def cmd_backup():
    backup_config()
    backups = list_backups()
    Style.success(f"Backup created. Total backups: {len(backups)}")


def cmd_restore(args):
    backups = list_backups()
    if not backups:
        Style.error("No backups found.")
        return
    if args.list:
        print(f"\n{Style.BOLD}{'#':<4} {'DATE':<20} {'FILE'}{Style.RESET}")
        print("-" * 60)
        for i, b in enumerate(backups, 1):
            try:
                mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(b.stat().st_mtime))
            except Exception:
                mtime = "unknown"
            print(f"{i:<4} {mtime:<20} {b.name}")
        print()
        return
    if args.index:
        idx = args.index - 1
        if 0 <= idx < len(backups):
            try:
                shutil.copy2(backups[idx], CONFIG_FILE)
                Style.success(f"Restored backup #{args.index}: {backups[idx].name}")
            except Exception as e:
                Style.error(f"Restore failed: {e}")
        else:
            Style.error(f"Backup #{args.index} not found. Use 'ftm restore --list' to see available.")
    else:
        restore_backup()


def cmd_reset(args=None):
    reset_to_defaults(force=getattr(args, 'force', False))


def _pull_dir(repo: str, gh_path: str, dest_dir: Path, extensions: tuple = (".jsonc",)):
    """Download all files with given extensions from a GitHub directory."""
    url = f"https://api.github.com/repos/{repo}/contents/{gh_path}"
    count = 0
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ftm-cli"})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
        if isinstance(data, dict) and "message" in data:
            return 0
        for item in data:
            if item.get("type") == "file" and item["name"].endswith(extensions):
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest = dest_dir / item["name"]
                with urllib.request.urlopen(item["download_url"]) as r, open(dest, "wb") as f:
                    f.write(r.read())
                count += 1
    except Exception:
        pass
    return count


def cmd_pull(args):
    ensure_dirs()
    repo = args.repo
    Style.info(f"Connecting to GitHub ({repo})...")

    total = 0

    # 1. Pull theme JSONC files
    count = _pull_dir(repo, "themes", USER_THEMES_DIR, (".jsonc",))
    if count > 0:
        Style.success(f"Downloaded {count} themes")
        total += count

    # 2. Pull theme images
    img_dir = USER_THEMES_DIR / "images"
    count = _pull_dir(repo, "themes/images", img_dir, (".txt", ".jpg", ".jpeg", ".png", ".gif"))
    if count > 0:
        Style.success(f"Downloaded {count} theme images")
        total += count

    # 3. Pull living-earth ASCII frames
    earth_dir = USER_THEMES_DIR / "living-earth"
    count = _pull_dir(repo, "themes/living-earth", earth_dir, (".txt",))
    if count > 0:
        Style.success(f"Downloaded {count} living-earth frames")
        total += count

    # 4. Pull scripts
    bin_dir = Path.home() / ".local" / "bin"
    count = _pull_dir(repo, "themes/scripts", bin_dir, (".sh",))
    if count > 0:
        bin_dir.mkdir(parents=True, exist_ok=True)
        for f in bin_dir.glob("*.sh"):
            f.chmod(0o755)
        Style.success(f"Downloaded {count} scripts to {bin_dir}")
        total += count

    if total == 0:
        Style.error("No assets found to download. Check the repo URL or try again later.")
    else:
        Style.success(f"Pull complete! Downloaded {total} assets total.")


def cmd_check():
    version = detect_fastfetch_version()
    if version:
        Style.success(f"fastfetch {version} detected")
    else:
        Style.error("fastfetch not found")
        mgr = detect_package_managers()
        if mgr:
            print(f"  Try: {Style.CYAN}{suggest_install('fastfetch')}{Style.RESET}")
        return
    pkg_managers = detect_package_managers()
    if pkg_managers:
        Style.success(f"Package managers: {', '.join(pkg_managers[:5])}" +
                      (f" and {len(pkg_managers) - 5} more" if len(pkg_managers) > 5 else ""))
    config_ok = CONFIG_FILE.exists()
    if config_ok:
        Style.success(f"Config exists: {CONFIG_FILE}")
    else:
        Style.warning("No config file. Try: ftm build  or  ftm set <theme>")
    themes = list_themes()
    Style.info(f"{len(themes)} theme(s) available")
    compat = FastfetchCompat()
    Style.info(f"Compatibility: fastfetch {compat.version_str()}")
    Style.info(f"Backups: {len(list_backups())}")


def cmd_modules(args):
    from ftm.moduledb import get_modules, MODULE_REGISTRY
    compat = FastfetchCompat()
    modules = MODULE_REGISTRY if args.all else get_modules(compat)
    cats = {}
    for m in modules:
        cats.setdefault(m.category, []).append(m)
    print(f"\n{Style.BOLD}All Modules — {'showing all' if args.all else f'compatible with fastfetch {compat.version_str()}'}{Style.RESET}")
    for cat in sorted(cats):
        print(f"\n{Style.CYAN}{cat.upper()}{Style.RESET}")
        for m in cats[cat]:
            ver = f" (v{m.since}+)" if m.since and args.all else ""
            sub = ""
            if args.all and m.sub_options:
                sub = f" [{', '.join(o.key for o in m.sub_options)}]"
            print(f"  {m.key:<25} {m.label}{Style.DIM}{ver}{sub}{Style.RESET}")
    print(f"\n{Style.DIM}Use --all to see all {len(MODULE_REGISTRY)} modules including version-incompatible ones.{Style.RESET}\n")


def cmd_help(args):
    docs = {
        "info": "Show system information including fastfetch version, OS distribution,\n       package managers, and theme counts.",
        "check": "Verify dependencies (fastfetch, fzf) and display system health summary.",
        "list": "List all discovered themes. Use --origin to filter by source (user,\n       system, example) or pass a search query.\n       Flags: --origin <type>, --query <text>",
        "search": "Alias for 'list --query <text>'. Quickly find themes by name.\n       Usage: ftm search <query>",
        "describe": "Show detailed information about a specific theme: origin, file size,\n       modification time, module list, logo type, and color settings.\n       Usage: ftm describe <theme>",
        "preview": "Preview a theme without applying it. Runs fastfetch with the theme\n       and its own module structure.\n       Usage: ftm preview <theme>",
        "pick": "Interactive theme picker using fzf. Browse themes with arrow keys,\n       live preview, and press ENTER to apply.\n       Requires: fzf",
        "set": "Apply a theme by name or path. Creates a backup automatically.\n       Usage: ftm set <theme>\n       Flags: --no-backup",
        "build": "Interactive theme builder wizard. Create custom themes step-by-step\n       with logo, colors, borders, and module selection with sub-options.",
        "edit": "Edit an existing theme. Loads the current config and walks through\n       the builder wizard to modify settings.\n       Usage: ftm edit <theme>",
        "export": "Export a theme to a file (default: current directory).\n       Usage: ftm export <theme> [output-path]",
        "import": "Import a theme from a file into your user themes directory.\n       Usage: ftm import <file>",
        "backup": "Create a manual backup of the current configuration.",
        "restore": "Restore or list backups.\n       Usage: ftm restore          (restore most recent)\n              ftm restore --list   (show all backups)\n              ftm restore -n <#>   (restore specific backup)",
        "reset": "Reset fastfetch configuration to system defaults.\n       A backup is created before resetting.",
        "pull": "Download community themes and assets from GitHub.\n       Usage: ftm pull [--repo owner/repo]\n       Pulls themes, images, ASCII frames, and scripts.",
        "modules": "List available fastfetch modules.\n       Use --all to include modules requiring newer fastfetch versions.",
        "help": "Show this detailed help. Use 'ftm help <command>' for specific info.\n       Usage: ftm help [command]",
    }
    topic = args.topic
    if topic and topic in docs:
        print(f"\n{Style.BOLD}ftm {topic}{Style.RESET}")
        print(f"{Style.DIM}{'-' * (4 + len(topic))}{Style.RESET}")
        print(f"  {docs[topic]}\n")
    else:
        print(f"\n{Style.BOLD}{APP_NAME} v{VERSION}{Style.RESET}")
        print(f"{Style.DIM}Professional CLI Theme Management for Fastfetch{Style.RESET}")
        print(f"\n{Style.CYAN}USAGE:{Style.RESET}")
        print("  ftm <command> [options]\n")
        print(f"{Style.CYAN}COMMANDS:{Style.RESET}")
        for cmd, desc in docs.items():
            if cmd == "help":
                continue
            first_line = desc.split('\n')[0]
            print(f"  {Style.GREEN}{cmd:<12}{Style.RESET} {first_line}")
        print(f"\n{Style.CYAN}EXAMPLES:{Style.RESET}")
        print(f"  {Style.DIM}ftm list                              {Style.RESET}List all themes")
        print(f"  {Style.DIM}ftm pick                              {Style.RESET}Browse themes interactively")
        print(f"  {Style.DIM}ftm set neofetch                      {Style.RESET}Apply a theme")
        print(f"  {Style.DIM}ftm build                             {Style.RESET}Create a new theme")
        print(f"  {Style.DIM}ftm edit my-theme                     {Style.RESET}Modify an existing theme")
        print(f"  {Style.DIM}ftm preview my-theme                  {Style.RESET}Preview without applying")
        print(f"  {Style.DIM}ftm describe my-theme                 {Style.RESET}Show theme details")
        print(f"  {Style.DIM}ftm export my-theme ~/backup.jsonc    {Style.RESET}Export a theme")
        print(f"  {Style.DIM}ftm import ~/downloaded-theme.jsonc   {Style.RESET}Import a theme")
        print(f"  {Style.DIM}ftm restore --list                    {Style.RESET}List backups")
        print(f"  {Style.DIM}ftm restore -n 3                      {Style.RESET}Restore specific backup")
        print()


def main():
    ensure_dirs()
    parser = argparse.ArgumentParser(
        description=f"{APP_NAME} v{VERSION}",
        add_help=False
    )

    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    subparsers.add_parser("info", help="Show system info")
    subparsers.add_parser("check", help="Check dependencies and system state")

    list_p = subparsers.add_parser("list", help="List themes")
    list_p.add_argument("--origin", "-o", choices=["user", "system", "example"], help="Filter by origin")
    list_p.add_argument("query", nargs="?", default=None, help="Search filter")

    search_p = subparsers.add_parser("search", help="Search themes")
    search_p.add_argument("query", help="Search term")

    describe_p = subparsers.add_parser("describe", help="Show theme details")
    describe_p.add_argument("theme", help="Theme name")

    preview_p = subparsers.add_parser("preview", help="Preview a theme")
    preview_p.add_argument("theme", help="Theme name or path")

    subparsers.add_parser("pick", help="Interactive fzf picker")

    set_p = subparsers.add_parser("set", help="Apply a theme")
    set_p.add_argument("theme", help="Theme name or path")
    set_p.add_argument("--no-backup", action="store_true", help="Skip backup")

    build_p = subparsers.add_parser("build", help="Build a new theme")
    build_p.add_argument("--advanced", "-a", action="store_true", help="Full customization")

    edit_p = subparsers.add_parser("edit", help="Edit an existing theme")
    edit_p.add_argument("theme", help="Theme name")

    export_p = subparsers.add_parser("export", help="Export a theme")
    export_p.add_argument("theme", help="Theme name")
    export_p.add_argument("output", nargs="?", help="Output path")

    import_p = subparsers.add_parser("import", help="Import a theme file")
    import_p.add_argument("file", help="Path to theme file")
    import_p.add_argument("--apply", action="store_true", help="Apply after import")

    subparsers.add_parser("backup", help="Create a backup")

    restore_p = subparsers.add_parser("restore", help="Restore from backup")
    restore_p.add_argument("--list", "-l", action="store_true", help="List backups")
    restore_p.add_argument("-n", "--index", type=int, help="Backup number to restore")

    reset_p = subparsers.add_parser("reset", help="Reset to defaults")
    reset_p.add_argument("-f", "--force", action="store_true", help="Skip confirmation")

    pull_p = subparsers.add_parser("pull", help="Download community themes from GitHub")
    pull_p.add_argument("--repo", default="tasavvuf/fastfetch-theme-manager", help="GitHub repo (owner/name)")
    pull_p.add_argument("--path", default="themes", help=argparse.SUPPRESS)

    mod_p = subparsers.add_parser("modules", help="List fastfetch modules")
    mod_p.add_argument("--all", action="store_true", help="Show all including incompatible")

    help_p = subparsers.add_parser("help", help="Show detailed help")
    help_p.add_argument("topic", nargs="?", default=None, help="Command name")

    if len(sys.argv) == 1:
        cmd = "help"
        args = help_p.parse_args(["--help"] if len(sys.argv) == 1 else [])
    else:
        args = parser.parse_args()

    dispatch = {
        "info": lambda: cmd_info(),
        "check": lambda: cmd_check(),
        "list": lambda: cmd_list(args),
        "search": lambda: cmd_search(args),
        "describe": lambda: cmd_describe(args),
        "preview": lambda: cmd_preview(args),
        "pick": lambda: cmd_pick(),
        "set": lambda: cmd_set(args),
        "build": lambda: cmd_build(),
        "edit": lambda: cmd_edit(args),
        "export": lambda: cmd_export(args),
        "import": lambda: cmd_import(args),
        "backup": lambda: cmd_backup(),
        "restore": lambda: cmd_restore(args),
        "reset": lambda: cmd_reset(args),
        "pull": lambda: cmd_pull(args),
        "modules": lambda: cmd_modules(args),
        "help": lambda: cmd_help(args),
    }

    try:
        dispatch.get(args.command, lambda: parser.print_help())()
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(0)
    except BrokenPipeError:
        pass


if __name__ == "__main__":
    main()
