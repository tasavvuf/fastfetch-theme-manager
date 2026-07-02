<div align="center">

# Fastfetch Theme Manager

### *Professional CLI Theme Management for Fastfetch*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-brightgreen.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20BSD-lightgrey)](https://github.com/tasavvuf/fastfetch-theme-manager)
[![Fastfetch](https://img.shields.io/badge/fastfetch-2.50+-blue)](https://github.com/fastfetch-cli/fastfetch)
[![Themes](https://img.shields.io/badge/themes-6%20original-8A2BE2)](https://github.com/tasavvuf/fastfetch-theme-manager/tree/main/themes)

**Created by [Tasavvuf Gori](https://github.com/tasavvuf)**

---

A professional, **zero-dependency** CLI tool to build, manage, and preview Fastfetch themes with version-aware module detection, crash protection, and universal distro support. Comes with **6 original ASCII art themes** ready to use.

[Features](#-features) [Installation](#-installation) [Usage](#-usage) [Theme Collection](#-theme-collection) [Contributing](CONTRIBUTING.md) [License](#-license)

</div>

---

## Features

- **6 Original ASCII Art Themes** — Hand-crafted ASCII art portraits and creatures
- **Interactive Theme Builder** — Create themes step-by-step with version-gated sub-options
- **70+ Supported Modules** — Auto-filtered to your fastfetch version
- **Universal Distro Support** — Detects 50+ package managers across all Linux distros, macOS, and BSDs
- **Version Compatibility Layer** — Automatically adapts to fastfetch 2.50 through 2.65+
- **Dynamic FZF Preview** — Live preview shows exactly your theme's module layout
- **Smart Safety System** — Automatic backups before changes, auto-revert on failure
- **Original Art Collection** — Dragons, beasts, and portraits as terminal logos
- **Zero Dependencies** — Pure Python 3 standard library

---

## Installation

### Option 1: One-Line Install

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/tasavvuf/fastfetch-theme-manager/main/install.sh)
```

### Option 2: pip Install

```bash
pip3 install --user git+https://github.com/tasavvuf/fastfetch-theme-manager.git
```

### Option 3: Manual

```bash
git clone https://github.com/tasavvuf/fastfetch-theme-manager.git
cd fastfetch-theme-manager
chmod +x install.sh
./install.sh
```

---

## Usage

```
ftm info        Show system info and fastfetch version
ftm check       Check dependencies and system state
ftm list        List all available themes
ftm search      Find themes by name
ftm describe    Show theme details and module list
ftm preview     Preview a theme without applying
ftm pick        Interactive fzf theme picker
ftm set NAME    Apply a specific theme
ftm build       Create a new theme interactively
ftm edit NAME   Modify an existing theme
ftm export      Export a theme to a file
ftm import      Import a theme from a file
ftm backup      Create a configuration backup
ftm restore     Restore from a backup
ftm reset       Reset to default configuration
ftm pull        Download community themes from GitHub
ftm modules     List modules compatible with your fastfetch version
```

### Quick Examples

```bash
# Browse and pick a theme interactively
ftm pick

# Apply a theme
ftm set ascii-art-5

# Preview without applying
ftm preview ascii-art

# Import a theme file
ftm import --apply themes/ascii-art.jsonc

# Export your current config as a theme
ftm export my-custom-theme

# List all themes from a specific source
ftm list --origin user
```

---

## Theme Collection

This project includes **6 original ASCII art themes**. Browse interactively with `ftm pick` or apply directly:


---

## Building with Sub-Options

When you build a theme with `ftm build`, the builder detects your fastfetch version and only shows compatible modules and sub-options:

```
? Configure Memory module:
  Exclude ZFS ARC from used memory? [Y/n]: y     (v2.65.2+)

? Configure GPU module:
  Enable driver-specific detection? [y/N]: y      (v2.65.0+)
  Show PCIe link speed? [Y/n]: n                  (v2.65.0+)
```

---

## Supported Platforms

| Operating System | Support | Package Managers |
|----------------|---------|-----------------|
| Arch Linux | Full | pacman, yay, paru, pacstall |
| Debian/Ubuntu | Full | apt, snap, linglong |
| Fedora/RHEL | Full | dnf, yum, rpm-ostree |
| openSUSE | Full | zypper |
| Gentoo/Funtoo | Full | emerge, eix |
| NixOS | Full | nix-env, nixos-rebuild |
| Guix System | Full | guix |
| Alpine Linux | Full | apk |
| Void Linux | Full | xbps-install |
| Solus | Full | eopkg |
| Clear Linux | Full | swupd |
| FreeBSD | Full | pkg, pkgtool |
| macOS | Full | brew, macports |
| NetBSD/OpenBSD | Full | pkgsrc, pkg_add |
| Haiku | Full | hpkg |
| And more... | Full | cargo, pip3, flatpak, snap, AppImage |

---

## Fastfetch Version Compatibility

| Feature | Minimum Version |
|---------|----------------|
| ZFS ARC memory exclusion | 2.65.2 |
| GPU PCIe link speed | 2.65.0 |
| CPU code name / technology | 2.65.0 |
| Display serial number, HDR | 2.65.0 |
| Codec module | 2.64.0 |
| Media playback progress | 2.63.0 |
| PhysicalDisk hide options | 2.62.0 |
| Keyboard module | 2.61.0 |
| Editor module, {cwd} | 2.60.0 |
| Wallpaper module | 2.57.0 |
| Dynamic interval | 2.55.0 |
| JSON5 config, march | 2.51.0 |
| All other modules | 2.50.0 |

---

## Requirements

| Requirement | Status | Notes |
|------------|--------|-------|
| Python 3.8+ | Required | Pre-installed on most systems |
| Fastfetch | Required | Tested with 2.50 through 2.65+ |
| fzf | Optional | Recommended for `ftm pick` |

---

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for full details.

---

<div align="center">

### ⭐ If you find FTM useful, consider giving it a star!

**Made with ❤️ by [Tasavvuf Gori](https://github.com/tasavvuf)**

[Report Issue](https://github.com/tasavvuf/fastfetch-theme-manager/issues) • [Request Feature](https://github.com/tasavvuf/fastfetch-theme-manager/issues) • [View Discussions](https://github.com/tasavvuf/fastfetch-theme-manager/discussions)

</div>
