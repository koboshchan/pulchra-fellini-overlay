from pathlib import Path
from platformdirs import user_config_dir
import subprocess

def config_directory():
    return Path(user_config_dir("pulchra-fellini-overlay", appauthor=False))

import ctypes
import os
import threading
import pystray
from pystray import MenuItem as item
from PIL import Image

image_background_alpha = 255

def configure_transparency(window):
    window.wm_attributes("-transparentcolor", "#FF00FF")
    window.configure(bg="#FF00FF")
    return "#FF00FF"

def open_folder(path):
    os.startfile(path)

def shape_window(root, image):
    pass

def set_click_through(root, enabled):
    hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
    styles = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
    styles = styles | (0x20 | 0x80000) if enabled else styles & ~0x20
    ctypes.windll.user32.SetWindowLongW(hwnd, -20, styles)
    return enabled

def idle_seconds():
    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]
    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(lii)
    if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
        return ((ctypes.windll.kernel32.GetTickCount() - lii.dwTime) & 0xffffffff) / 1000
    return 0.0

def setup_tray(self):
    script_dir = self.get_script_dir()
    icon_path = str(Path(getattr(__import__("sys"), "_MEIPASS", Path(__file__).resolve().parent.parent)) / "assets" / "pulchra_overlay_icon.ico")
    try: tray_img = Image.open(icon_path)
    except Exception: tray_img = Image.new("RGBA", (64, 64), (255, 0, 255, 255))
    
    tray_menu = pystray.Menu(
        item('Select Costume', pystray.Menu(
            item('Standing', lambda: self.root.after(0, lambda: self.change_costume("pulchra_overlay_standing.png")), checked=lambda item: self.current_image_filename == "pulchra_overlay_standing.png"),
            item('Sitting', lambda: self.root.after(0, lambda: self.change_costume("pulchra_overlay_sitting.png")), checked=lambda item: self.current_image_filename == "pulchra_overlay_sitting.png"),
            item('Casual', lambda: self.root.after(0, lambda: self.change_costume("pulchra_overlay_casual.png")), checked=lambda item: self.current_image_filename == "pulchra_overlay_casual.png"),
            item('Action 1', lambda: self.root.after(0, lambda: self.change_costume("pulchra_overlay_action_1.png")), checked=lambda item: self.current_image_filename == "pulchra_overlay_action_1.png"),
            item('Action 2', lambda: self.root.after(0, lambda: self.change_costume("pulchra_overlay_action_2.png")), checked=lambda item: self.current_image_filename == "pulchra_overlay_action_2.png"),
            item('No mask Action', lambda: self.root.after(0, lambda: self.change_costume("pulchra_nomask_action.png")), checked=lambda item: self.current_image_filename == "pulchra_nomask_action.png"),
            item('No mask Sitting', lambda: self.root.after(0, lambda: self.change_costume("pulchra_nomask_sitting.png")), checked=lambda item: self.current_image_filename == "pulchra_nomask_sitting.png"),
            item('Petting tail', lambda: self.root.after(0, lambda: self.change_costume("pulchra_overlay_tail.png")), checked=lambda item: self.current_image_filename == "pulchra_overlay_tail.png"),
            item('Thinking', lambda: self.root.after(0, lambda: self.change_costume("pulchra_overlay_thinking.png")), checked=lambda item: self.current_image_filename == "pulchra_overlay_thinking.png"),
            item('Burnt', lambda: self.root.after(0, lambda: self.change_costume("pulchra_overlay_burnt.png")), checked=lambda item: self.current_image_filename == "pulchra_overlay_burnt.png")
        )),
        item('Select Dialogue Mood', pystray.Menu(
            item('Casual Mode', lambda: self.toggle_tray_mood("casual"), checked=lambda item: self.mood_states["casual"].get()),
            item('Work Mode', lambda: self.toggle_tray_mood("work"), checked=lambda item: self.mood_states["work"].get()),
            item('Coding Mode', lambda: self.toggle_tray_mood("coding"), checked=lambda item: self.mood_states["coding"].get()),
            item('Gaming Mode', lambda: self.toggle_tray_mood("gaming"), checked=lambda item: self.mood_states["gaming"].get()),
            item('Relaxed Mode', lambda: self.toggle_tray_mood("relaxed"), checked=lambda item: self.mood_states["relaxed"].get()),
            item('Focus Mode', lambda: self.toggle_tray_mood("focus"), checked=lambda item: self.mood_states["focus"].get()),
            item('Late-Night Mode', lambda: self.toggle_tray_mood("late_night"), checked=lambda item: self.mood_states["late_night"].get()),
            pystray.Menu.SEPARATOR,
            item('All On', lambda: self.root.after(0, self.master_mood_all_on)),
            item('All Off', lambda: self.root.after(0, self.master_mood_all_off))
        )),

        pystray.Menu.SEPARATOR,
        item('Change Proxy Name...', lambda: self.root.after(0, self.prompt_custom_name)),
        item('Open Settings Dashboard...', lambda: self.root.after(0, self.open_settings_dashboard)),
        pystray.Menu.SEPARATOR,
        item('Scale size', pystray.Menu(

            item('Tiny (50%)', lambda: self.root.after(0, lambda: self.change_size(0.5))),
            item('Small (75%)', lambda: self.root.after(0, lambda: self.change_size(0.75))),
            item('Normal (100%)', lambda: self.root.after(0, lambda: self.change_size(1.0))),
            item('Comfortable (125%)', lambda: self.root.after(0, lambda: self.change_size(1.25))),
            item('Medium (150%)', lambda: self.root.after(0, lambda: self.change_size(1.5))),
            item('Large (175%)', lambda: self.root.after(0, lambda: self.change_size(1.75))),
            item('Huge (200%)', lambda: self.root.after(0, lambda: self.change_size(2.0)))
        )),
        item('Opacity Level', pystray.Menu(
            item("Hidden", lambda: self.root.after(0, lambda: self.change_opacity_live(0))),
            item("25%", lambda: self.root.after(0, lambda: self.change_opacity_live(0.25))),
            item("50%", lambda: self.root.after(0, lambda: self.change_opacity_live(0.50))),
            item("75%", lambda: self.root.after(0, lambda: self.change_opacity_live(0.75))),
            item("100%", lambda: self.root.after(0, lambda: self.change_opacity_live(1.0)))
        )),
        item('Alarm Options', pystray.Menu(
            item('Set Alarm...', lambda: self.root.after(0, self.prompt_custom_alarm)),
            item('Clear Active Alarm', lambda: self.root.after(0, self.clear_active_alarm))
        )),
        item('Start Contract Timer', pystray.Menu(
            item('5 Minute Break', lambda: self.root.after(0, lambda: self.start_commission_timer(5))),
            item('25 Minute Work', lambda: self.root.after(0, lambda: self.start_commission_timer(25))),
            item('1 Hour Grind', lambda: self.root.after(0, lambda: self.start_commission_timer(60))),
            pystray.Menu.SEPARATOR,
            item('Set Custom Timer...', lambda: self.root.after(0, self.prompt_custom_timer))
        )),
        pystray.Menu.SEPARATOR,
        item('Get Intel', lambda: self.root.after(0, self.force_chat_bubble)),
        item('System Pulse Check', lambda: self.root.after(0, self.trigger_pulse_check)),
        item('Toggle Chat Bubbles', lambda: self.safe_tray_toggle_chat(), checked=lambda item: self.chat_enabled), 
        item('Toggle Click Irritation', lambda: self.safe_tray_toggle_irritation(), checked=lambda item: self.var_irritation.get()),           
        item('Toggle Resource Monitor', lambda: self.safe_tray_toggle_monitor(), checked=lambda item: self.monitor_enabled),
        item('Toggle Edge Patrol Walks', lambda: self.safe_tray_toggle_patrol(), checked=lambda item: self._patrol_state),
        item('Toggle Auto-Costume Swap', lambda: self.safe_tray_toggle_swapper(), checked=lambda item: self._swapper_state),
        item('Toggle Drag Lock', lambda: self.safe_tray_toggle_pin(), checked=lambda item: self.is_pinned),
        item('Toggle Click-Through', lambda: self.safe_tray_toggle_click(), checked=lambda item: self.is_click_through),
        item('Flip Direction (Mirror)', lambda: self.root.after(0, self.toggle_flip)),
        pystray.Menu.SEPARATOR,
        item('Snap to Node', pystray.Menu(
            item('Top Left Corner', lambda: self.root.after(0, lambda: self.snap_to_screen_node("top_left"))),
            item('Top Center Edge', lambda: self.root.after(0, lambda: self.snap_to_screen_node("top_center"))),
            item('Top Right Corner', lambda: self.root.after(0, lambda: self.snap_to_screen_node("top_right"))),
            item('Middle Left Edge', lambda: self.root.after(0, lambda: self.snap_to_screen_node("middle_left"))),
            item('Middle Right Edge', lambda: self.root.after(0, lambda: self.snap_to_screen_node("middle_right"))),
            item('Bottom Left Corner', lambda: self.root.after(0, lambda: self.snap_to_screen_node("bottom_left"))),
            item('Bottom Center Edge', lambda: self.root.after(0, lambda: self.snap_to_screen_node("bottom_center"))),
            item('Bottom Right Anchor', lambda: self.root.after(0, lambda: self.snap_to_screen_node("bottom_right")))
        )),
        item("Send to Bottom Right", lambda: self.root.after(0, lambda: self.snap_to_screen_node("bottom_right"))),
        item("Snap to Nearest Node", lambda: self.root.after(0, self.snap_to_closest_node)),
        item('Walk to Node', pystray.Menu(
            item('Top Left Corner', lambda: self.root.after(0, lambda: self.route_perimeter_walk("top_left"))),
            item('Top Center Edge', lambda: self.root.after(0, lambda: self.route_perimeter_walk("top_center"))),
            item('Top Right Corner', lambda: self.root.after(0, lambda: self.route_perimeter_walk("top_right"))),
            item('Middle Left Edge', lambda: self.root.after(0, lambda: self.route_perimeter_walk("middle_left"))),
            item('Middle Right Edge', lambda: self.root.after(0, lambda: self.route_perimeter_walk("middle_right"))),
            item('Bottom Left Corner', lambda: self.root.after(0, lambda: self.route_perimeter_walk("bottom_left"))),
            item('Bottom Center Edge', lambda: self.root.after(0, lambda: self.route_perimeter_walk("bottom_center"))),
            item('Bottom Right Anchor', lambda: self.root.after(0, lambda: self.route_perimeter_walk("bottom_right")))
        )),
        item("Go to Home Anchor", lambda: self.root.after(0, self.go_to_home_anchor)),
        item('DVD Bouncing Mode', lambda: self.safe_tray_toggle_dvd(), checked=lambda item: self.is_dvd_mode),
        item('Disable Edge Snapping', lambda: self.safe_tray_toggle_snap(), checked=lambda item: self.var_disable_snap.get()), # <-- NEW
        item('Open Folder Path', lambda: self.root.after(0, self.open_folder)),
        item('Reset Settings to Default', lambda: self.safe_tray_call_reset()),
        item('Cancel Active Patrol', lambda: self.root.after(0, self.cancel_active_walk)),
        pystray.Menu.SEPARATOR,
        item('Close Companion', lambda: self.root.after(0, self.quit_application))
    )
    self.tray_icon = pystray.Icon("PulchraCompanion", tray_img, "Pulchra Desktop Companion", tray_menu)
    threading.Thread(target=self.tray_icon.run, daemon=True).start()
