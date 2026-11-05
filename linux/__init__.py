from pathlib import Path
from platformdirs import user_config_dir
import subprocess

def config_directory():
    return Path(user_config_dir("pulchra-fellini-overlay", appauthor=False))

import sys
image_background_alpha = 0

def configure_transparency(window):
    window.configure(bg="#202020")
    return "#202020"

def open_folder(path):
    subprocess.Popen(["xdg-open", str(path)])

def set_click_through(root, enabled):
    return False

def idle_seconds():
    return 0.0

def setup_tray(app):
    # Many Linux desktops have no status-icon host; all controls remain in the context menu.
    pass

def shape_window(root, image):
    try:
        from Xlib import display, X
        from Xlib.ext import shape
        if not hasattr(shape_window, "display"):
            shape_window.display = display.Display()
        root.update_idletasks()
        window = shape_window.display.create_resource_object("window", root.winfo_id())
        parent = window.query_tree().parent
        alpha = image.getchannel("A")
        rectangles = []
        for y in range(image.height):
            start = None
            for x in range(image.width + 1):
                solid = x < image.width and alpha.getpixel((x, y)) >= 128
                if solid and start is None:
                    start = x
                elif not solid and start is not None:
                    rectangles.append((start, y, x - start, 1))
                    start = None
        for target in (window, parent):
            target.shape_rectangles(shape.SO.Set, shape.SK.Bounding,
                                    X.Unsorted, 0, 0, rectangles)
        shape_window.display.sync()
    except Exception as error:
        # XWayland generally works; native Wayland may use a rectangular fallback.
        print("X11 transparency unavailable:", error, file=sys.stderr)
