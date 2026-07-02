import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ftm.fastfetch_version import FastfetchVersion, FastfetchCompat
from ftm.moduledb import get_modules, get_module_by_key, get_available_sub_options


def test_get_modules_v65():
    compat = FastfetchCompat(FastfetchVersion(2, 65, 2))
    modules = get_modules(compat)
    keys = {m.key for m in modules}
    assert "codec" in keys
    assert "editor" in keys
    assert "keyboard" in keys
    assert "wallpaper" in keys
    assert "memory" in keys
    assert "gpu" in keys
    assert "title" in keys


def test_get_modules_v55():
    compat = FastfetchCompat(FastfetchVersion(2, 55, 0))
    modules = get_modules(compat)
    keys = {m.key for m in modules}
    assert "codec" not in keys
    assert "editor" not in keys
    assert "keyboard" not in keys
    assert "wallpaper" not in keys
    assert "title" in keys
    assert "memory" in keys


def test_get_module_by_key():
    compat = FastfetchCompat(FastfetchVersion(2, 65, 2))
    mod = get_module_by_key("gpu", compat)
    assert mod is not None
    assert mod.key == "gpu"
    assert mod.label == "GPU"


def test_sub_options():
    compat = FastfetchCompat(FastfetchVersion(2, 65, 2))
    opts = get_available_sub_options("gpu", compat)
    opt_keys = {o.key for o in opts}
    assert "driverSpecific" in opt_keys
    assert "pcieMaxSpeed" in opt_keys
    assert "pcieCurrSpeed" in opt_keys

    opts_v50 = get_available_sub_options("gpu", FastfetchCompat(FastfetchVersion(2, 50, 0)))
    opt_v50_keys = {o.key for o in opts_v50}
    assert "driverSpecific" not in opt_v50_keys
    assert "pcieMaxSpeed" not in opt_v50_keys


def test_memory_sub_options():
    compat = FastfetchCompat(FastfetchVersion(2, 65, 2))
    opts = get_available_sub_options("memory", compat)
    opt_keys = {o.key for o in opts}
    assert "zfsArc" in opt_keys

    opts_v64 = get_available_sub_options("memory", FastfetchCompat(FastfetchVersion(2, 64, 0)))
    opt_v64_keys = {o.key for o in opts_v64}
    assert "zfsArc" not in opt_v64_keys


if __name__ == "__main__":
    test_get_modules_v65()
    test_get_modules_v55()
    test_get_module_by_key()
    test_sub_options()
    test_memory_sub_options()
    print("All moduledb tests passed!")
