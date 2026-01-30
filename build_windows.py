import os
import sys
import subprocess
from pathlib import Path


def find_tcl_tk_dirs() -> tuple[str | None, str | None]:
    # In most Python installs, tcl/tk live under base_prefix\tcl\tcl8.6 and base_prefix\tcl\tk8.6
    base = Path(sys.base_prefix)
    tcl_root = base / "tcl"
    if not tcl_root.exists():
        return None, None

    tcl_dir = None
    tk_dir = None
    for child in tcl_root.iterdir():
        name = child.name.lower()
        if child.is_dir() and name.startswith("tcl"):
            tcl_dir = str(child)
        if child.is_dir() and name.startswith("tk"):
            tk_dir = str(child)
    return tcl_dir, tk_dir


def main():
    tcl_dir, tk_dir = find_tcl_tk_dirs()
    if not tcl_dir or not tk_dir:
        print("No se encontraron carpetas tcl/tk en el Python base.")
        sys.exit(1)

    # Build command with add-data for Tkinter runtime
    cmd = [
        "flet",
        "build",
        "windows",
        "--clear-cache",
        "--cleanup-app",
        "--cleanup-packages",
        "--add-data",
        f"{tcl_dir};tcl",
        "--add-data",
        f"{tk_dir};tk",
    ]

    print("Ejecutando:", " ".join(cmd))
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
