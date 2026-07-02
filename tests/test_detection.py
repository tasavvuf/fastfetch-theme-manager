import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ftm.detection import detect_distro, DistroInfo, detect_package_managers


def test_detect_distro():
    info = detect_distro()
    assert isinstance(info, DistroInfo)
    assert isinstance(info.id, str)
    assert isinstance(info.id_like, list)


def test_detect_package_managers():
    pm = detect_package_managers()
    assert isinstance(pm, list)


if __name__ == "__main__":
    test_detect_distro()
    test_detect_package_managers()
    info = detect_distro()
    print(f"Detected distro: {info.pretty_name or info.id} ({info.version_id})")
    print(f"Package managers: {', '.join(detect_package_managers())}")
    print("All detection tests passed!")
