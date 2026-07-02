import shutil
import os
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class DistroInfo:
    id: str = ""
    id_like: List[str] = None
    version: str = ""
    version_id: str = ""
    pretty_name: str = ""
    codename: str = ""

    def __post_init__(self):
        if self.id_like is None:
            self.id_like = []


def detect_distro() -> DistroInfo:
    info = DistroInfo()
    os_release_paths = ["/etc/os-release", "/usr/lib/os-release"]
    for path in os_release_paths:
        if os.path.exists(path):
            try:
                with open(path) as f:
                    for line in f:
                        line = line.strip()
                        if "=" not in line:
                            continue
                        key, _, value = line.partition("=")
                        value = value.strip('"\'')
                        if key == "ID":
                            info.id = value.lower()
                        elif key == "ID_LIKE":
                            info.id_like = [v.strip().lower() for v in value.split()]
                        elif key == "VERSION":
                            info.version = value
                        elif key == "VERSION_ID":
                            info.version_id = value
                        elif key == "PRETTY_NAME":
                            info.pretty_name = value
                        elif key == "VERSION_CODENAME":
                            info.codename = value
            except Exception:
                pass
            break
    return info


def detect_package_managers() -> List[str]:
    found = []
    checks = [
        "apt", "apt-get", "pacman", "dnf", "yum", "zypper",
        "emerge", "eix", "nix-env", "nixos-rebuild", "guix",
        "eopkg", "swupd", "rpm-ostree", "apk", "xbps-install",
        "pkg", "pacstall", "pisi", "paludis", "cargo", "pip3",
        "brew", "snap", "flatpak",
        "cards", "kiss", "moss", "porg", "install-release",
        "opkg", "scoop", "winget", "choco", "macports",
        "hpkg", "mport", "pkgtool", "pkgsrc",
        "lpkg", "soar", "sorcery", "linglong",
    ]
    for cmd in checks:
        if shutil.which(cmd) or shutil.which(f"/usr/bin/{cmd}"):
            found.append(cmd)
    return found


def suggest_install(pkg: str) -> str:
    mgr = detect_package_managers()
    suggestions = {
        "apt": f"sudo apt install {pkg}",
        "pacman": f"sudo pacman -S {pkg}",
        "dnf": f"sudo dnf install {pkg}",
        "yum": f"sudo yum install {pkg}",
        "zypper": f"sudo zypper install {pkg}",
        "emerge": f"sudo emerge --ask {pkg}",
        "nix-env": f"nix-env -iA nixos.{pkg}",
        "guix": f"sudo guix install {pkg}",
        "eopkg": f"sudo eopkg install {pkg}",
        "swupd": f"sudo swupd bundle-add {pkg}",
        "apk": f"sudo apk add {pkg}",
        "xbps-install": f"sudo xbps-install -S {pkg}",
        "pkg": f"sudo pkg install {pkg}",
        "brew": f"brew install {pkg}",
        "cargo": f"cargo install {pkg}",
        "pip3": f"pip3 install {pkg}",
        "snap": f"sudo snap install {pkg}",
        "flatpak": f"flatpak install {pkg}",
    }
    for m in mgr:
        if m in suggestions:
            return suggestions[m]
    full = "sudo apt install" if shutil.which("apt") else \
           "sudo pacman -S" if shutil.which("pacman") else \
           "sudo dnf install" if shutil.which("dnf") else \
           "sudo zypper install" if shutil.which("zypper") else \
           "sudo emerge --ask" if shutil.which("emerge") else \
           "sudo apk add" if shutil.which("apk") else \
           "sudo xbps-install -S" if shutil.which("xbps-install") else \
           "brew install" if shutil.which("brew") else ""
    if full:
        return f"{full} {pkg}"
    return f"Please install '{pkg}' using your package manager."
