import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ftm.fastfetch_version import FastfetchVersion, FastfetchCompat


def test_version_parsing():
    v = FastfetchVersion(2, 65, 2)
    assert str(v) == "2.65.2"


def test_version_comparison():
    assert FastfetchVersion(2, 65, 2) > FastfetchVersion(2, 65, 1)
    assert FastfetchVersion(2, 65, 0) >= FastfetchVersion(2, 65, 0)
    assert FastfetchVersion(2, 64, 0) < FastfetchVersion(2, 65, 0)
    assert FastfetchVersion(2, 65, 2) >= FastfetchVersion(2, 65, 0)
    assert FastfetchVersion(1, 0, 0) < FastfetchVersion(2, 0, 0)
    assert FastfetchVersion(3, 0, 0) > FastfetchVersion(2, 99, 99)


def test_compat_features():
    compat = FastfetchCompat(FastfetchVersion(2, 65, 2))
    assert compat.supports("zfs_arc_memory")
    assert compat.supports("gpu_pcie_speed")
    assert compat.supports("gpu_driver_specific")
    assert compat.supports("cpu_code_name")
    assert compat.supports("display_serial")
    assert compat.supports("list_data_paths")
    assert compat.supports("structure_flag")
    assert compat.supports("codec_module")
    assert compat.supports("editor_module")
    assert compat.supports("keyboard_module")
    assert compat.supports("wallpaper_module")
    assert compat.supports("march_detection")
    assert compat.supports("display_disable_linewrap")
    assert compat.supports("media_progress")


def test_compat_older():
    compat = FastfetchCompat(FastfetchVersion(2, 55, 0))
    assert not compat.supports("zfs_arc_memory")
    assert not compat.supports("gpu_pcie_speed")
    assert not compat.supports("cpu_code_name")
    assert not compat.supports("codec_module")
    assert not compat.supports("editor_module")
    assert not compat.supports("wallpaper_module")
    assert compat.supports("dynamic_interval")
    assert compat.supports("parallel_commands")
    assert compat.supports("list_data_paths")


def test_compat_v50():
    compat = FastfetchCompat(FastfetchVersion(2, 50, 0))
    assert compat.supports("case_sensitive_keys")
    assert compat.supports("zpool_module")
    assert not compat.supports("march_detection")
    assert not compat.supports("btrfs_module")
    assert not compat.supports("title_cwd")


if __name__ == "__main__":
    test_version_parsing()
    test_version_comparison()
    test_compat_features()
    test_compat_older()
    test_compat_v50()
    print("All version tests passed!")
