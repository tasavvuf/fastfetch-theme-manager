#!/usr/bin/env python3
# Fastfetch Theme Manager v3.0.0
import sys
import os

def find_ftm_package():
    launcher = os.path.abspath(__file__)

    # 1. Next to launcher as src/ftm/ (development layout)
    p = os.path.join(os.path.dirname(launcher), "src", "ftm")
    if os.path.isdir(p) and os.path.isfile(os.path.join(p, "cli.py")):
        sys.path.insert(0, os.path.join(os.path.dirname(launcher), "src"))
        return True

    # 2. Next to launcher as ../lib/ftm/ftm/ (installed layout)
    p = os.path.join(os.path.dirname(launcher), "..", "lib", "ftm", "ftm")
    if os.path.isdir(p) and os.path.isfile(os.path.join(p, "cli.py")):
        sys.path.insert(0, os.path.join(os.path.dirname(launcher), "..", "lib", "ftm"))
        return True

    # 3. In ../lib/python*/site-packages/ftm/ (pip install layout)
    for d in os.listdir("/usr/local/lib" if sys.platform != "win32" else os.environ.get("LOCALAPPDATA", "")):
        sd = os.path.join("/usr/local/lib", d, "site-packages")
        if os.path.isdir(os.path.join(sd, "ftm")):
            sys.path.insert(0, sd)
            return True
    for d in os.listdir(os.path.expanduser("~/.local/lib")):
        sd = os.path.join(os.path.expanduser("~/.local/lib"), d, "site-packages")
        if os.path.isdir(os.path.join(sd, "ftm")):
            sys.path.insert(0, sd)
            return True

    return False

if __name__ == "__main__":
    if find_ftm_package():
        from ftm.cli import main
        main()
    else:
        print("Error: Could not locate the ftm package.")
        print("Install it with: pip install --user git+https://github.com/itz-dev-tasavvuf/fastfetch-theme-manager.git")
        print("Or run from the source tree: python3 -m ftm <command> (from src/)")
        sys.exit(1)
