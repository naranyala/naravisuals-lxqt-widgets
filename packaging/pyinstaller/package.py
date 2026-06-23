#!/usr/bin/env python3
"""NaraVisuals PyInstaller Packager - Build standalone executables."""
import subprocess
import sys
import os
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent.parent
BUILD_DIR = PROJECT_DIR / "dist"

APPS = {
    "nv-manager": {
        "module": "naravisuals.manager.control_center",
        "desc": "Control Center",
    },
    "nv-manager-legacy": {
        "module": "naravisuals.manager.app",
        "desc": "Settings Hub (Legacy)",
    },
    "nv-theme-store": {
        "module": "naravisuals.theme_manager.app",
        "desc": "Theme Manager",
    },
    "nv-desktop-manager": {
        "module": "naravisuals.desktop_manager.app",
        "desc": "Desktop Manager",
    },
    "nv-sddm-manager": {
        "module": "naravisuals.sddm_manager.app",
        "desc": "SDDM Manager",
    },
}

HIDDEN_IMPORTS = [
    "naravisuals",
    "naravisuals.core",
    "naravisuals.core.theme_engine",
    "naravisuals.core.config_manager",
    "naravisuals.core.base_widget",
    "naravisuals.core.async_utils",
    "naravisuals.manager",
    "naravisuals.manager.control_center",
    "naravisuals.manager.app",
    "naravisuals.theme_manager",
    "naravisuals.theme_manager.app",
    "naravisuals.desktop_manager",
    "naravisuals.desktop_manager.app",
    "naravisuals.sddm_manager",
    "naravisuals.sddm_manager.app",
    "naravisuals.widgets",
    "naravisuals.data_providers",
    "naravisuals.daemon",
    "psutil",
    "requests",
    "dbus",
    "notify2",
    "PyQt6",
    "PyQt6.QtWidgets",
    "PyQt6.QtCore",
    "PyQt6.QtGui",
]


def check_pyinstaller():
    try:
        result = subprocess.run(["pyinstaller", "--version"],
                                capture_output=True, text=True)
        print(f"PyInstaller {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("PyInstaller not found. Install with: pip install pyinstaller")
        return False


def build_app(name: str, info: dict, extra_args: list[str] | None = None):
    print(f"\n{'='*50}")
    print(f"Building: {name} ({info['desc']})")
    print(f"{'='*50}")

    entry_script = BUILD_DIR / f"build_entry_{name}.py"
    entry_script.write_text(f"""\
import sys
import os
sys.path.insert(0, "{PROJECT_DIR}")
from {info['module']} import main
main()
""")

    cmd = [
        "pyinstaller",
        "--name", name,
        "--onefile",
        "--windowed",
        "--noconfirm",
        "--clean",
        "--distpath", str(BUILD_DIR),
        "--workpath", str(BUILD_DIR / "build" / name),
        "--specpath", str(BUILD_DIR / "specs"),
    ]

    for hi in HIDDEN_IMPORTS:
        cmd.extend(["--hidden-import", hi])

    cmd.extend(["--collect-all", "naravisuals"])
    cmd.extend(["--paths", str(PROJECT_DIR)])

    if extra_args:
        cmd.extend(extra_args)

    cmd.append(str(entry_script))

    result = subprocess.run(cmd, capture_output=True, text=True)

    entry_script.unlink(missing_ok=True)

    output = BUILD_DIR / name
    if output.exists():
        size = output.stat().st_size
        if size > 1024 * 1024:
            size_str = f"{size / (1024*1024):.1f} MB"
        else:
            size_str = f"{size / 1024:.0f} KB"
        print(f"  -> {output} ({size_str})")
        return True
    else:
        print(f"  FAILED: {name}")
        if result.stderr:
            print(f"  Error: {result.stderr[-500:]}")
        return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Build NaraVisuals standalone executables")
    parser.add_argument("apps", nargs="*", default=list(APPS.keys()),
                        help="Apps to build (default: all)")
    parser.add_argument("--clean", action="store_true", help="Clean build artifacts first")
    parser.add_argument("--list", action="store_true", help="List available apps")
    args = parser.parse_args()

    if args.list:
        print("Available apps:")
        for name, info in APPS.items():
            print(f"  {name:25s} {info['desc']}")
        return

    if not check_pyinstaller():
        sys.exit(1)

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    (BUILD_DIR / "specs").mkdir(exist_ok=True)

    if args.clean:
        import shutil
        for name in args.apps:
            d = BUILD_DIR / "build" / name
            if d.exists():
                shutil.rmtree(d)
        print("Cleaned build artifacts.\n")

    print(f"\nProject: {PROJECT_DIR}")
    print(f"Output:  {BUILD_DIR}\n")

    results = []
    for name in args.apps:
        if name in APPS:
            ok = build_app(name, APPS[name])
            results.append((name, ok))
        else:
            print(f"Unknown app: {name}")

    print(f"\n{'='*50}")
    print("Build Summary")
    print(f"{'='*50}\n")

    for name, ok in results:
        status = "OK" if ok else "FAILED"
        print(f"  [{status}] {name}")

    print(f"\nOutput directory: {BUILD_DIR}")
    print(f"\nTo install:")
    print(f"  sudo cp {BUILD_DIR}/nv-* /usr/local/bin/")


if __name__ == "__main__":
    main()
