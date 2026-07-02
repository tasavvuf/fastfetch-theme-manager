# Contributing to Fastfetch Theme Manager

Thanks for considering contributing to FTM!

[Report Bugs](#reporting-bugs) • [Suggest Features](#suggesting-enhancements) • [Submit Themes](#submitting-themes) • [Code Guidelines](#code-contributions)

---

## Reporting Bugs

**Before Submitting:**
- Search existing issues to avoid duplicates
- Verify you're using the latest version (`python3 ftm.py --version`)

**Include:**
- OS/Distro and version
- Python version (`python3 --version`)
- Fastfetch version (`fastfetch --version`)
- Steps to reproduce and expected vs actual behavior
- Full error output

---

## Suggesting Enhancements

Be specific about the feature, its use case, and why it's valuable. Include mockups if applicable.

---

## Submitting Themes

### Structure

Place your ASCII art file in `themes/images/` and create a matching `.jsonc` theme file in `themes/`:

```
themes/
  your-theme.jsonc
  images/
    your-art.txt
```

### Theme File Template

```jsonc
{
  "$schema": "https://github.com/fastfetch-cli/fastfetch/raw/dev/doc/json_schema.json",
  "logo": {
    "type": "file-raw",
    "source": "/absolute/path/to/your-art.txt"
  },
  "display": {
    "separator": " : ",
    "color": "white"
  },
  "modules": [
    "title", "separator", "os", "host", "kernel", "uptime",
    "packages", "shell", "de", "terminal",
    "cpu", "gpu", "memory",
    "break", "colors"
  ]
}
```

### Requirements

- Theme is a `.jsonc` file in `themes/`
- ASCII art is a `.txt` file in `themes/images/`
- Use `"type": "file-raw"` to display raw text (not processed)
- Use absolute paths in `source` if your filename has spaces
- Tested with `fastfetch --config themes/your-theme.jsonc`

---

## Code Contributions

### Architecture Overview (v3.0+)

FTM v3 is structured as a Python package under `src/ftm/`:

```
src/ftm/
  __init__.py       # Package metadata, version
  __main__.py       # python3 -m ftm entry point
  cli.py            # CLI parser, command dispatch, help system
  config.py         # Paths, directory management
  style.py          # ANSI styling
  utils.py          # JSONC I/O, subprocess helpers
  fastfetch_version.py  # Version detection + compat database
  moduledb.py       # 70-module registry with version gating
  detection.py      # OS/distro/50+ package manager detection
  themes.py         # Theme discovery, listing, resolution
  manager.py        # Apply/backup/restore/reset
  builder.py        # Interactive theme builder wizard
  picker.py         # fzf TUI picker
```

### The Golden Rule: Zero Dependencies

FTM uses only Python standard library. No `pip install` required.

```
# DO NOT use:
import requests      # NO
import rich          # NO
import click         # NO
import pyyaml        # NO

# USE instead:
import urllib.request   # YES
import subprocess       # YES
import json             # YES
import shutil           # YES
```

### Coding Standards

1. **Type hints** for all function signatures
2. **No bare excepts** — always specify exception types
3. **f-strings** over `%` or `.format()` for string formatting
4. **Pathlib** over `os.path` for path operations
5. **No hardcoded paths** — use `shutil.which()`, config constants
6. **Error messages** use `Style` class, not raw `print()`

### Adding a New Module

1. Add the module definition to `moduledb.py` `MODULE_REGISTRY` list
2. Add a `ModuleDef` with key, label, category, `since` version, and any sub-options
3. Add the fastfetch version feature flag in `fastfetch_version.py` if the module requires a specific version

### Adding a New Package Manager

1. Add the binary name to `detection.py` `detect_package_managers()` checks list
2. Add the install command to `detection.py` `suggest_install()` dict
3. Add to `install.sh` package manager detection chain

### Adding a New Command

1. Add the subparser in `cli.py` `main()` function
2. Add the handler function (e.g., `cmd_mycommand`)
3. Add to the `dispatch` dictionary
4. Add docs entry in `cmd_help()` docs dict

### Version Database

When new fastfetch versions add features:
1. Add a new feature key to `fastfetch_version.py` `_build_table()`
2. Add the `FastfetchVersion` target
3. Reference the feature in `moduledb.py` via `since=FastfetchVersion(x,y,z)` or in sub-options

### Testing

```bash
# Run all tests
python3 -m pytest tests/

# Manual integration tests
python3 -m ftm check
python3 -m ftm list
python3 -m ftm info
```

### Development Workflow

```bash
git checkout -b feature/your-feature
# Make changes
python3 -m pytest tests/   # Run unit tests
python3 -m ftm check       # Run integration
git add .
git commit -m "feat: Your feature description"
git push origin feature/your-feature
```

### Commit Message Guidelines

| Prefix | Usage |
|--------|-------|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation |
| `refactor:` | Code restructuring |
| `test:` | Adding tests |
| `compat:` | Version compatibility updates |

### Pull Request Checklist

- [ ] No pip packages required
- [ ] All tests pass
- [ ] Errors handled gracefully (no raw tracebacks)
- [ ] Code uses type hints
- [ ] Tested with `python3 src/ftm/__main__.py check`
- [ ] If adding module support, updated `moduledb.py`
- [ ] If adding distro support, updated `detection.py` and `install.sh`

---

## Questions?

- Check existing issues labeled `good first issue`
- Ask in Discussions
- Open an issue with the `question` label
