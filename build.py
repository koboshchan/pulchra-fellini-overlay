"""Build the shared entry point using the native host's Python and architecture."""
import subprocess
import sys

args = [
    sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
    "--name", "Pulchra", "--onedir", "--add-data", "assets:assets",
    "--hidden-import", "PIL._tkinter_finder", "--hidden-import", "windows", "--hidden-import", "mac", "--hidden-import", "linux",
]
if sys.platform in ("win32", "darwin"):
    args.append("--windowed")
if sys.platform == "win32":
    args += ["--icon", "assets/pulchra_overlay_icon.ico"]
subprocess.run(args + ["pulchra.py"], check=True)
