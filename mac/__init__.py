from pathlib import Path
from platformdirs import user_config_dir
import subprocess

def config_directory():
    return Path(user_config_dir("pulchra-fellini-overlay", appauthor=False))

image_background_alpha = 0

def configure_transparency(window):
    window.wm_attributes("-transparent", True)
    window.configure(bg="systemTransparent")
    return "systemTransparent"

def open_folder(path):
    subprocess.Popen(["open", str(path)])

def shape_window(root, image):
    pass

def set_click_through(root, enabled):
    # Tk does not expose NSWindow ignoresMouseEvents; keep the pet recoverable.
    return False

def idle_seconds():
    return 0.0

def setup_tray(app):
    # Cocoa requires ownership of the main loop. Tk context menu supplies all controls.
    pass
