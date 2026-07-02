import re
import shutil
from dataclasses import dataclass
from typing import Optional


@dataclass
class FastfetchVersion:
    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __ge__(self, other: "FastfetchVersion") -> bool:
        if self.major != other.major:
            return self.major >= other.major
        if self.minor != other.minor:
            return self.minor >= other.minor
        return self.patch >= other.patch

    def __gt__(self, other: "FastfetchVersion") -> bool:
        if self.major != other.major:
            return self.major > other.major
        if self.minor != other.minor:
            return self.minor > other.minor
        return self.patch > other.patch

    def __le__(self, other: "FastfetchVersion") -> bool:
        return not self.__gt__(other)

    def __lt__(self, other: "FastfetchVersion") -> bool:
        return not self.__ge__(other)

    def __eq__(self, other: "FastfetchVersion") -> bool:
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)


_V = FastfetchVersion


class FastfetchCompat:
    """Version compatibility database for fastfetch features."""

    def __init__(self, version: Optional[FastfetchVersion] = None):
        self.version = version or detect_fastfetch_version()

    def supports(self, feature: str) -> bool:
        table = self._build_table()
        if feature not in table:
            return False
        required = table[feature]
        if required is None:
            return self.version is not None
        return self.version is not None and self.version >= required

    def require(self, feature: str) -> FastfetchVersion:
        table = self._build_table()
        return table.get(feature, FastfetchVersion(99, 99, 99))

    def _build_table(self) -> dict:
        return {
            "list_data_paths": _V(2, 10, 0),
            "gen_config_force": _V(2, 10, 0),
            "structure_flag": _V(2, 10, 0),
            "jsonc_config": _V(2, 10, 0),
            "json5_config": _V(2, 51, 0),
            "module_conditions": _V(2, 51, 0),
            "dynamic_interval": _V(2, 55, 0),
            "parallel_commands": _V(2, 55, 0),
            "logo_padding_bottom": _V(2, 64, 0),
            "structure_disabled": _V(2, 58, 0),
            "json_flag": _V(2, 54, 0),
            "case_sensitive_keys": _V(2, 50, 0),
            "zfs_arc_memory": _V(2, 65, 2),
            "gpu_pcie_speed": _V(2, 65, 1),
            "gpu_driver_specific": _V(2, 65, 1),
            "cpu_code_name": _V(2, 65, 0),
            "cpu_technology": _V(2, 65, 0),
            "cpu_show_pe_core_count": _V(2, 65, 0),
            "display_serial": _V(2, 65, 0),
            "display_hdr": _V(2, 65, 0),
            "display_disable_linewrap": _V(2, 65, 0),
            "display_scale_factor": _V(2, 52, 0),
            "gpu_egl_ext": _V(2, 65, 0),
            "localip_ipv6_type": _V(2, 53, 0),
            "disk_folder_glob": _V(2, 54, 0),
            "disk_array_folders": _V(2, 53, 0),
            "disk_size_free_available": _V(2, 53, 0),
            "separator_times": _V(2, 53, 0),
            "title_cwd": _V(2, 60, 0),
            "title_user_id": _V(2, 59, 0),
            "physicaldisk_hide_virtual": _V(2, 62, 0),
            "physicaldisk_hide_unused": _V(2, 62, 0),
            "physicalmemory_show_empty": _V(2, 61, 0),
            "codec_module": _V(2, 64, 0),
            "editor_module": _V(2, 60, 0),
            "keyboard_module": _V(2, 61, 0),
            "wallpaper_module": _V(2, 57, 0),
            "bluetooth_module": _V(2, 61, 0),
            "logo_module": _V(2, 57, 0),
            "media_progress": _V(2, 63, 0),
            "command_split_lines": _V(2, 56, 0),
            "display_fraction": _V(2, 52, 0),
            "march_detection": _V(2, 51, 0),
            "numa_nodes": _V(2, 56, 0),
            "btrfs_module": _V(2, 52, 0),
            "zpool_module": _V(2, 50, 0),
            "porg_packages": _V(2, 65, 0),
            "install_release_packages": _V(2, 65, 0),
            "moss_packages": _V(2, 60, 0),
            "kiss_packages": _V(2, 56, 0),
            "cards_packages": _V(2, 63, 0),
            "appimage_packages": _V(2, 62, 0),
            "pci_eeprom_module": _V(2, 50, 0),
        }

    def version_str(self) -> str:
        return str(self.version) if self.version else "unknown"


def detect_fastfetch_version() -> Optional[FastfetchVersion]:
    fastfetch_path = shutil.which("fastfetch")
    if not fastfetch_path:
        return None
    try:
        import subprocess
        result = subprocess.run(
            [fastfetch_path, "--version"],
            capture_output=True, text=True, timeout=5
        )
        output = result.stdout.strip() or result.stderr.strip()
        if not output:
            return None
        match = re.search(r"(\d+)\.(\d+)\.(\d+)", output)
        if match:
            return FastfetchVersion(
                int(match.group(1)),
                int(match.group(2)),
                int(match.group(3))
            )
    except Exception:
        pass
    return None
