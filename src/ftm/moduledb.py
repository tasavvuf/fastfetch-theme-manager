from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from ftm.fastfetch_version import FastfetchVersion, FastfetchCompat


@dataclass
class SubOption:
    label: str
    key: str
    type: str = "bool"
    default: Any = True
    since: Optional[FastfetchVersion] = None
    jsonschema_key: Optional[str] = None


@dataclass
class ModuleDef:
    key: str
    label: str
    category: str
    since: Optional[FastfetchVersion] = None
    sub_options: List[SubOption] = field(default_factory=list)
    description: str = ""


MODULE_REGISTRY: List[ModuleDef] = [
    ModuleDef("title", "Title (User@Host)", "info", description="User name and host name"),
    ModuleDef("separator", "Separator", "visual", description="Visual separator line"),
    ModuleDef("os", "OS", "system", description="Operating system info"),
    ModuleDef("host", "Host", "system", description="Host/device name"),
    ModuleDef("kernel", "Kernel", "system", description="Kernel version"),
    ModuleDef("uptime", "Uptime", "time", description="System uptime"),
    ModuleDef("packages", "Packages", "system", description="Installed package count"),
    ModuleDef("shell", "Shell", "env", description="Current shell"),
    ModuleDef("de", "DE/WM", "env", description="Desktop environment"),
    ModuleDef("terminal", "Terminal", "env", description="Terminal emulator"),
    ModuleDef("cpu", "CPU", "system", description="Processor info",
              sub_options=[
                  SubOption("Show P-Core/E-Core count", "showPeCoreCount",
                            since=FastfetchVersion(2, 65, 0), jsonschema_key="showPeCoreCount"),
                  SubOption("Show CPU code name", "codeName",
                            since=FastfetchVersion(2, 65, 0), jsonschema_key="codeName"),
                  SubOption("Show CPU manufacturing technology", "technology",
                            since=FastfetchVersion(2, 65, 0), jsonschema_key="technology"),
                  SubOption("Show temperature", "temperature",
                            default=False, jsonschema_key="temperature"),
              ]),
    ModuleDef("gpu", "GPU", "system", description="Graphics card info",
              sub_options=[
                  SubOption("Enable driver-specific detection", "driverSpecific",
                            since=FastfetchVersion(2, 65, 1), jsonschema_key="driverSpecific"),
                  SubOption("Show PCIe link speed (max)", "pcieMaxSpeed",
                            since=FastfetchVersion(2, 65, 1), jsonschema_key="pcieMaxSpeed"),
                  SubOption("Show PCIe link speed (current)", "pcieCurrSpeed",
                            since=FastfetchVersion(2, 65, 1), jsonschema_key="pcieCurrSpeed"),
                  SubOption("Show driver name", "driver", jsonschema_key="driver"),
                  SubOption("Show temperature", "temperature",
                            default=False, jsonschema_key="temperature"),
              ]),
    ModuleDef("memory", "Memory", "system", description="RAM usage",
              sub_options=[
                  SubOption("Exclude ZFS ARC from used memory", "zfsArc",
                            since=FastfetchVersion(2, 65, 2), jsonschema_key="zfsArc",
                            default=False),
              ]),
    ModuleDef("disk", "Disk", "disk", description="Disk usage",
              sub_options=[
                  SubOption("Show free size", "showFree",
                            since=FastfetchVersion(2, 53, 0), jsonschema_key="showFree"),
                  SubOption("Show available size", "showAvailable",
                            since=FastfetchVersion(2, 53, 0), jsonschema_key="showAvailable"),
              ]),
    ModuleDef("battery", "Battery", "power", description="Battery status",
              sub_options=[
                  SubOption("Show temperature", "temperature",
                            default=False, jsonschema_key="temperature"),
                  SubOption("Show cycle count", "cycleCount",
                            jsonschema_key="cycleCount"),
              ]),
    ModuleDef("localip", "Local IP", "network", description="Local IP addresses",
              sub_options=[
                  SubOption("Show IPv6 address", "showIpv6",
                            since=FastfetchVersion(2, 53, 0), jsonschema_key="showIpv6"),
                  SubOption("Show MAC address", "showMac", jsonschema_key="showMac"),
                  SubOption("Default route only", "defaultRouteOnly",
                            jsonschema_key="defaultRouteOnly"),
              ]),
    ModuleDef("display", "Display", "display", description="Display/monitor info",
              sub_options=[
                  SubOption("Show serial number", "serial",
                            since=FastfetchVersion(2, 65, 0), jsonschema_key="serial"),
                  SubOption("Show HDR compatibility", "hdrCompatible",
                            since=FastfetchVersion(2, 65, 0), jsonschema_key="hdrCompatible"),
                  SubOption("Show scale factor", "scaleFactor",
                            since=FastfetchVersion(2, 52, 0), jsonschema_key="scaleFactor"),
              ]),
    ModuleDef("break", "Break (Space)", "visual", description="Line break/spacer"),
    ModuleDef("colors", "Colors (Palette)", "visual", description="Color palette"),

    ModuleDef("swap", "Swap", "system", description="Swap memory usage",
              since=FastfetchVersion(2, 50, 0)),
    ModuleDef("processes", "Processes", "system", description="Running process count",
              since=FastfetchVersion(2, 50, 0)),
    ModuleDef("datetime", "Date/Time", "time", description="Current date and time",
              since=FastfetchVersion(2, 50, 0),
              sub_options=[
                  SubOption("Use 12-hour format", "amPm",
                            since=FastfetchVersion(2, 63, 0), jsonschema_key="amPm"),
              ]),
    ModuleDef("locale", "Locale", "locale", description="System locale",
              since=FastfetchVersion(2, 50, 0)),
    ModuleDef("users", "Users", "system", description="Logged-in users",
              since=FastfetchVersion(2, 50, 0)),
    ModuleDef("version", "Version (fastfetch)", "info", description="Fastfetch version info",
              since=FastfetchVersion(2, 50, 0)),
    ModuleDef("wm", "Window Manager", "env", description="Window manager",
              since=FastfetchVersion(2, 50, 0)),
    ModuleDef("wmtheme", "WM Theme", "env", description="Window manager theme",
              since=FastfetchVersion(2, 64, 0)),
    ModuleDef("theme", "Theme (GTK/Qt)", "theme", description="System theme",
              since=FastfetchVersion(2, 50, 0)),
    ModuleDef("icons", "Icons", "theme", description="Icon theme",
              since=FastfetchVersion(2, 50, 0)),
    ModuleDef("cursor", "Cursor", "theme", description="Cursor theme",
              since=FastfetchVersion(2, 50, 0)),
    ModuleDef("fonts", "Fonts", "theme", description="System fonts",
              since=FastfetchVersion(2, 50, 0)),
    ModuleDef("wallpaper", "Wallpaper", "theme", description="Desktop wallpaper",
              since=FastfetchVersion(2, 57, 0)),
    ModuleDef("terminalfont", "Terminal Font", "env", description="Terminal font",
              since=FastfetchVersion(2, 50, 0)),
    ModuleDef("terminalsize", "Terminal Size", "env", description="Terminal dimensions",
              since=FastfetchVersion(2, 50, 0)),
    ModuleDef("terminaltheme", "Terminal Theme", "env", description="Terminal color scheme",
              since=FastfetchVersion(2, 50, 0)),
    ModuleDef("sound", "Sound/Audio", "media", description="Sound devices",
              since=FastfetchVersion(2, 50, 0)),
    ModuleDef("bluetooth", "Bluetooth", "network", description="Bluetooth devices",
              since=FastfetchVersion(2, 61, 0)),
    ModuleDef("wifi", "Wi-Fi", "network", description="Wi-Fi connection info",
              since=FastfetchVersion(2, 50, 0)),
    ModuleDef("editor", "Editor", "env", description="Default text editor",
              since=FastfetchVersion(2, 60, 0)),
    ModuleDef("keyboard", "Keyboard", "peripheral", description="Keyboard devices",
              since=FastfetchVersion(2, 61, 0)),
    ModuleDef("mouse", "Mouse", "peripheral", description="Mouse devices",
              since=FastfetchVersion(2, 53, 0)),
    ModuleDef("gamepad", "Gamepad", "peripheral", description="Gamepad controllers",
              since=FastfetchVersion(2, 53, 0)),
    ModuleDef("monitor", "Monitor", "display", description="Monitor info",
              since=FastfetchVersion(2, 50, 0)),
    ModuleDef("codec", "Codec (Video)", "media", description="Hardware video codecs",
              since=FastfetchVersion(2, 64, 0),
              sub_options=[
                  SubOption("Show encoder/decoder type", "showType", jsonschema_key="showType"),
                  SubOption("Use Vulkan for detection", "useVulkan",
                            jsonschema_key="useVulkan", default=False),
              ]),
    ModuleDef("diskio", "Disk I/O", "disk", description="Disk read/write stats",
              since=FastfetchVersion(2, 50, 0)),
    ModuleDef("physicaldisk", "Physical Disk", "disk", description="Physical disk info",
              since=FastfetchVersion(2, 50, 0),
              sub_options=[
                  SubOption("Show virtual disks", "hideVirtual",
                            since=FastfetchVersion(2, 62, 0),
                            jsonschema_key="hideVirtual", default=False),
              ]),
    ModuleDef("physicalmemory", "RAM Modules", "system", description="Physical memory slots",
              since=FastfetchVersion(2, 50, 0),
              sub_options=[
                  SubOption("Show empty slots", "showEmptySlots",
                            since=FastfetchVersion(2, 61, 0), jsonschema_key="showEmptySlots"),
              ]),
    ModuleDef("poweradapter", "Power Adapter", "power", description="Power adapter info",
              since=FastfetchVersion(2, 50, 0)),
    ModuleDef("chassis", "Chassis", "system", description="System chassis type",
              since=FastfetchVersion(2, 58, 0)),
    ModuleDef("bios", "BIOS", "system", description="BIOS/UEFI info",
              since=FastfetchVersion(2, 50, 0)),
    ModuleDef("board", "Motherboard", "system", description="Motherboard info",
              since=FastfetchVersion(2, 50, 0)),
    ModuleDef("bootmgr", "Boot Manager", "system", description="Boot manager info",
              since=FastfetchVersion(2, 57, 0)),
    ModuleDef("btrfs", "Btrfs", "disk", description="Btrfs filesystem info",
              since=FastfetchVersion(2, 52, 0)),
    ModuleDef("zpool", "ZFS Pool", "disk", description="ZFS pool info",
              since=FastfetchVersion(2, 50, 0)),
    ModuleDef("publicip", "Public IP", "network", description="Public IP address",
              since=FastfetchVersion(2, 50, 0)),
    ModuleDef("media", "Media (Playing)", "media", description="Currently playing media",
              since=FastfetchVersion(2, 50, 0),
              sub_options=[
                  SubOption("Show playback progress", "progress",
                            since=FastfetchVersion(2, 63, 0), jsonschema_key="progress"),
              ]),
    ModuleDef("command", "Command Output", "custom", description="Custom command output",
              since=FastfetchVersion(2, 50, 0),
              sub_options=[
                  SubOption("Split output into lines", "splitLines",
                            since=FastfetchVersion(2, 56, 0), jsonschema_key="splitLines"),
              ]),
    ModuleDef("camera", "Camera", "peripheral", description="Camera devices",
              since=FastfetchVersion(2, 50, 0)),
    ModuleDef("cpuusage", "CPU Usage", "system", description="CPU usage percentage",
              since=FastfetchVersion(2, 50, 0)),
    ModuleDef("cpucache", "CPU Cache", "system", description="CPU cache info",
              since=FastfetchVersion(2, 50, 0)),
    ModuleDef("loadavg", "Load Average", "system", description="System load average",
              since=FastfetchVersion(2, 50, 0)),
    ModuleDef("initsystem", "Init System", "system", description="Init system (systemd, etc.)",
              since=FastfetchVersion(2, 50, 0)),
    ModuleDef("opencl", "OpenCL", "system", description="OpenCL info",
              since=FastfetchVersion(2, 50, 0)),
    ModuleDef("opengl", "OpenGL", "system", description="OpenGL info",
              since=FastfetchVersion(2, 50, 0)),
    ModuleDef("vulkan", "Vulkan", "system", description="Vulkan info",
              since=FastfetchVersion(2, 50, 0)),
    ModuleDef("brightness", "Brightness", "display", description="Display brightness",
              since=FastfetchVersion(2, 50, 0)),
    ModuleDef("weather", "Weather", "network", description="Weather info",
              since=FastfetchVersion(2, 50, 0)),
    ModuleDef("dns", "DNS", "network", description="DNS servers",
              since=FastfetchVersion(2, 50, 0)),
    ModuleDef("netio", "Network I/O", "network", description="Network traffic stats",
              since=FastfetchVersion(2, 50, 0)),
    ModuleDef("tpm", "TPM", "system", description="Trusted Platform Module",
              since=FastfetchVersion(2, 50, 0)),
]


def get_modules(compat: Optional[FastfetchCompat] = None) -> List[ModuleDef]:
    if compat is None:
        compat = FastfetchCompat()
    available = []
    for mod in MODULE_REGISTRY:
        if mod.since is None:
            available.append(mod)
        elif compat.version is not None and compat.version >= mod.since:
            available.append(mod)
    return available


def get_module_by_key(key: str, compat: Optional[FastfetchCompat] = None) -> Optional[ModuleDef]:
    for mod in get_modules(compat):
        if mod.key == key:
            return mod
    return None


def get_available_sub_options(mod_key: str, compat: Optional[FastfetchCompat] = None) -> List[SubOption]:
    mod = get_module_by_key(mod_key, compat)
    if not mod:
        return []
    if compat is None:
        compat = FastfetchCompat()
    return [opt for opt in mod.sub_options
            if opt.since is None or (compat.version is not None and compat.version >= opt.since)]
