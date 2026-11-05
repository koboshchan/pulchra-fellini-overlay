import os
import sys
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog  
from PIL import Image, ImageTk
import random
import time
import json
import math
import shutil
import subprocess
from pathlib import Path
from core.platforms import platform_support

try:
    import psutil
except ImportError:
    psutil = None

def get_asset_path(relative_path):
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    return str(base / "assets" / relative_path)


resource_path = get_asset_path


configure_transparency = platform_support.configure_transparency


class PulchraDesktopCompanion:
    def __init__(self, root):
        self.root = root

        # --- 1. CORE RENDER & APP WINDOW METRICS ---
        self.target_height = 300  
        self.current_scale = 1.0  
        self.current_image_filename = "pulchra_overlay_standing.png"
        self.current_opacity = 1.0
        self.saved_x = None
        self.saved_y = None
        self.home_x = None
        self.home_y = None
        self._pre_irritation_costume = "pulchra_overlay_standing.png"

        # --- 2. CONFIG BOOLEANS & FLAGS ---
        self.is_pinned = False
        self.is_click_through = False
        self.is_flipped = False
        self.chat_enabled = False
        self.monitor_enabled = False
        self._swapper_state = True
        self._patrol_state = True
        self.is_dvd_mode = False
        self.dvd_dx = 5
        self.dvd_dy = 5
        self._dvd_loop_id = None
        self.head_shortcut_setting = "chat"

        self.click_irritation_enabled = True  # Default to True, config handles loading it later
        self.bubble_light_mode_enabled = False
        self.trust_frozen_enabled = False

        # --- 5. ALERT ALARMS & COMMISSION CONTRACT TIMERS ---
        # ... your existing trackers ...
        self.click_streak_count = 0
        self.last_click_timestamp = 0.0


        # --- 3. MOOD CONFIGURATION PROFILES ---
        # Options: "casual", "work", "coding", "gaming", "relaxed", "focus", "late_night", "all"
        self.current_mood_selection = "casual"  

        # --- 4. ENGINE TIMER DEBRIS & HARDWARE BASELINES ---
        self.last_net_bytes_recv = None
        self.last_net_bytes_sent = None
        self.last_net_check_time = None
        self.last_pulse_bytes_recv = None
        self.last_pulse_bytes_sent = None
        self.last_cpu_alert_time = 0
        self.last_ram_alert_time = 0
        self.last_battery_alert_time = 0

        # --- 5. ALERT ALARMS & COMMISSION CONTRACT TIMERS ---
        self.alarm_time_str = None
        self.alarm_triggered_today = False
        self.timer_seconds_left = 0

        # --- 6. BACKGROUND WORKER & LOOP TICK HANDLES ---
        self.bubble_window = None
        self.chat_timer_id = None
        self.auto_hide_id = None
        self.timer_loop_id = None
        self.monitor_loop_id = None
        self._active_glide_id = None
        self._walk_loop_id = None
        self._costume_swapper_id = None 

        self.mood_states = {
            "casual": tk.BooleanVar(value=True),
            "work": tk.BooleanVar(value=False),
            "coding": tk.BooleanVar(value=False),
            "gaming": tk.BooleanVar(value=False),
            "relaxed": tk.BooleanVar(value=False),
            "focus": tk.BooleanVar(value=False),
            "late_night": tk.BooleanVar(value=False)
        }

        self.user_name = "Proxy"  # Default name

        # --- LOAD DATA PROFILES FROM FILE ARCHIVES ---
        self.load_config_profile()

        # --- 7. TKINTER COMPATIBLE VARIABLE REGISTER ---
        self.var_chat = tk.BooleanVar(value=self.chat_enabled)
        self.var_monitor = tk.BooleanVar(value=self.monitor_enabled)
        self.var_pinned = tk.BooleanVar(value=self.is_pinned)
        self.var_click_through = tk.BooleanVar(value=self.is_click_through)
        self.var_swapper = tk.BooleanVar(value=self._swapper_state)
        self.var_patrol = tk.BooleanVar(value=self._patrol_state)
        self.var_mood_selection = tk.StringVar(value=self.current_mood_selection)
        self.var_irritation = tk.BooleanVar(value=self.click_irritation_enabled)
        self.var_freeze_trust = tk.BooleanVar(value=self.trust_frozen_enabled)
        
        # Correctly assigned initialized state configuration variables
        self.var_bubble_light_mode = tk.BooleanVar(value=self.bubble_light_mode_enabled)
        self.var_dvd_mode = tk.BooleanVar(value=self.is_dvd_mode)
        self.var_disable_snap = tk.BooleanVar(value=False)
        
        # Individual instance interval cooldown trackers
        self.var_cooldown_time = tk.IntVar(value=30)
        self.var_walk_cooldown = tk.IntVar(value=300)
        self.var_swap_cooldown = tk.IntVar(value=300)
        self.var_afk_cooldown = tk.IntVar(value=300)
        self.var_chat_cooldown = tk.IntVar(value=30)
        self.var_monitor_cooldown = tk.IntVar(value=180)


        self.load_config_profile()

        # --- MULTI-COSTUME BOUNDING BOX DICTIONARY MATRIX ---
        # Format: "filename": ( (head_x1, head_y1, head_x2, head_y2), (tail_x1, tail_y1, tail_x2, tail_y2) )
        self.costume_click_zones = {
            "pulchra_overlay_standing.png": (
                (0.36, 0.02, 0.64, 0.18),  # Head (Top center)
                (0.24, 0.60, 0.46, 0.82)   # Tail (Peeking left hip background)
            ),
            "pulchra_overlay_sitting.png": (
                (0.62, 0.03, 0.86, 0.22),  # Head (Leaning top right)
                (0.18, 0.26, 0.44, 0.50)   # Tail (Curled fluff high left)
            ),
            "pulchra_overlay_casual.png": (
                (0.66, 0.03, 0.90, 0.22),  # Head (Top right angled)
                (0.30, 0.18, 0.52, 0.42)   # Tail (Fluff behind back left)
            ),
            "pulchra_overlay_burnt.png": (
                (0.36, 0.02, 0.70, 0.26),  # Head (Large ears top center)
                (0.08, 0.54, 0.46, 0.76)   # Tail (Smoking tail low left)
            ),
            "pulchra_overlay_action_1.png": (
                (0.40, 0.06, 0.60, 0.22),  # Head (Centered top)
                (0.52, 0.55, 0.72, 0.74)   # Tail (Low right background)
            ),
            "pulchra_overlay_action_2.png": (
                (0.42, 0.08, 0.62, 0.26),  # Head (Ears up center-right)
                (0.06, 0.46, 0.38, 0.72)   # Tail (Massive low-left plume)
            ),
            "pulchra_nomask_action.png": (
                (0.42, 0.03, 0.60, 0.18),  # Head (No mask center)
                (0.56, 0.58, 0.74, 0.76)   # Tail (Behind gun right)
            ),
            "pulchra_nomask_sitting.png": (
                (0.70, 0.02, 0.94, 0.22),  # Head (Top right corner)
                (0.20, 0.22, 0.42, 0.48)   # Tail (Left shoulder side)
            ),
            "pulchra_overlay_tail.png": (
                (0.40, 0.02, 0.68, 0.18),  # Head (Top center-right)
                (0.26, 0.24, 0.68, 0.48)   # Tail (Cradled directly in arms)
            ),
            "pulchra_overlay_thinking.png": (
                (0.42, 0.02, 0.66, 0.18),  # Head (Top center)
                (0.58, 0.58, 0.76, 0.80)   # Tail (Peeking lower right edge)
            )
        }

        # --- HITBOX OVERRIDE ALIAS KEYS ---
        for key in list(self.costume_click_zones.keys()):
            base_name = key.replace(".png", "")
            self.costume_click_zones[base_name] = self.costume_click_zones[key]

        # --- AFK STATE INITIALIZATION ---
        self.is_afk = False
        self.afk_loop_id = None
        self._pre_afk_costume = "pulchra_overlay_standing.png"
        self._was_swapper_enabled_pre_afk = True
        self.root.after(5000, self.start_afk_sentinel_loop)

        # --- LOAD EXTERNAL PHRASE DATA POOLS ---
        self.phrases = []
        self.load_external_phrases()
        self.costume_quotes = {}
        self.load_external_costume_quotes()

        # --- 8. GRAPHICAL INTERFACE WINDOW COMPOSITING ---
        self.root.overrideredirect(True)           
        self.root.wm_attributes("-topmost", True)      
        self.bg_color = configure_transparency(self.root)

        self.label = tk.Label(root, bg=self.bg_color, bd=0)
        self.label.pack()

        self.spritesheet_path = get_asset_path("pulchra_walk_spritesheet.png")
        self.row_indices = {"down": 0, "left": 1, "right": 2, "up": 3}
        self._walking_photo_cache = {}

        if os.path.exists(self.spritesheet_path):
            sheet_img = Image.open(self.spritesheet_path).convert("RGBA")
            orig_cell_w = sheet_img.width // 8
            orig_cell_h = sheet_img.height // 4
            
            for direction, row_idx in self.row_indices.items():
                self._walking_photo_cache[direction] = []
                for col_idx in range(8):
                    x = col_idx * orig_cell_w
                    y = row_idx * orig_cell_h
                    crop_box = (x, y, x + orig_cell_w, y + orig_cell_h)
                    frame_crop = sheet_img.crop(crop_box)
                    
                    if frame_crop.getbbox():
                        content_box = frame_crop.getbbox()
                        frame_crop = frame_crop.crop(content_box)
                        
                        datas = frame_crop.get_flattened_data()
                        smooth_data = []
                        for px in datas:
                            # CRITICAL FIX: Kill anti-aliased semi-transparent magenta edges completely
                            if px[3] < 110:
                                smooth_data.append((255, 0, 255, 0))
                            else:
                                smooth_data.append(px)
                        frame_crop.putdata(smooth_data)
                        self._walking_photo_cache[direction].append(frame_crop)

        # --- INITIAL IMAGE & LAYOUT COORDINATE DISPATCH ---
        self.load_and_scale_image(initial_run=True)
        self.trigger_boot_greeting()

        # --- 9. TRIGGER RUNTIME AUTOMATION TIMERS ---
        if self.monitor_enabled and psutil is not None:
            self.monitor_loop_id = self.root.after(2000, self.run_resource_check)
        self._time_sentinel_id = self.root.after(1000, self.start_time_sentinel_loop)
        
        if self._swapper_state:
            self._costume_swapper_id = self.root.after(self.var_swap_cooldown.get() * 1000, self.start_costume_swapper_loop)
        if self.chat_enabled:
            self.chat_timer_id = self.root.after(self.var_chat_cooldown.get() * 1000, self.trigger_chat_bubble)
        if self.var_patrol.get():
            self._walk_loop_id = self.root.after(self.var_walk_cooldown.get() * 1000, self.start_random_walk_loop)

            
        self._clip_loop_id = self.root.after(3000, self.start_clipboard_monitor_loop)


        # --- 10. OS WINDOW CONTROLS & EVENT BOUNDARIES ---
        self.label.bind("<Button-1>", self.start_drag)
        self.label.bind("<B1-Motion>", self.drag_window)
        self.label.bind("<ButtonRelease-1>", self.end_drag_save)
        self.label.bind("<Button-3>", self.show_context_menu)
        self.label.bind("<Button-2>", self.show_context_menu)        

        self.create_context_menu()
        if "--smoke-test" not in sys.argv:
            self.setup_system_tray()
        self.root.bind("<Escape>", lambda e: self.quit_application())


    def get_script_dir(self):
        directory = platform_support.config_directory()
        directory.mkdir(parents=True, exist_ok=True)
        for name in ("pulchra_mood_quotes.json", "pulchra_costumes.json"):
            target = directory / name
            if not target.exists():
                shutil.copyfile(get_asset_path(name), target)
        return str(directory)

    def shape_linux_window(self, image):
        platform_support.shape_window(self.root, image)

    def show_credits(self):
        messagebox.showinfo("About Pulchra",
                            "Original author: gugoxiii ultimatedanx\n"
                            "Published with the author's permission.\n"
                            "https://sites.google.com/view/pulchra-fellini-overlay")

    def _obfuscate_trust(self, val):
        # XOR encryption loop with structural bitmasking key (0x5A)
        # Prevents raw Notepad edits by transforming data into a hexadecimal token
        key = 0x5A
        return hex(int(val) ^ key)[2:].zfill(2).upper()

    def _deobfuscate_trust(self, hex_str):
        try:
            key = 0x5A
            cleaned_hex = str(hex_str).strip()
            return int(cleaned_hex, 16) ^ key
        except Exception:
            return None 

    
    def get_trust_tier_label(self):
        if self.trust_points < 40:
            return "low"
        elif self.trust_points >= 150:
            return "high"
        return "neutral"


    def load_config_profile(self):
        script_dir = self.get_script_dir()
        config_path = os.path.join(script_dir, "config.json")
        
        # --- SAFE INITIALIZATION BASELINE ---
        if not hasattr(self, 'trust_points'):
            self.trust_points = 50  # Default baseline if file missing entirely

        if os.path.exists(config_path):
            # Give the OS up to 5 quick attempts to read if a thread lock occurs
            for _ in range(5):
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        cfg = json.load(f)
                    
                    # Core values
                    self.current_scale = cfg.get("scale", 1.0)
                    self.current_image_filename = cfg.get("costume", "pulchra_overlay_standing.png")
                    self.is_pinned = cfg.get("pinned", False)
                    self.is_click_through = cfg.get("click_through", False)
                    self.is_flipped = cfg.get("flipped", False)
                    self.current_opacity = cfg.get("opacity", 1.0)
                    self.chat_enabled = cfg.get("chat_enabled", False)
                    self.monitor_enabled = cfg.get("monitor_enabled", False)
                    self.saved_x = cfg.get("x", None)
                    self.saved_y = cfg.get("y", None)
                    self.home_x = cfg.get("home_x", None)
                    self.home_y = cfg.get("home_y", None)
                    self.alarm_time_str = cfg.get("alarm_time_str", None)
                    self._swapper_state = cfg.get("swapper_enabled", True)
                    self._patrol_state = cfg.get("patrol_enabled", True)
                    self.click_irritation_enabled = cfg.get("click_irritation_enabled", True)
                    self.user_name = cfg.get("user_name", "Proxy") 
                    self.last_login_date = cfg.get("last_login_date", None)
                    self.head_shortcut_setting = cfg.get("head_shortcut_setting", "chat")
                    if hasattr(self, 'var_freeze_trust'): self.var_freeze_trust.set(cfg.get("trust_frozen_enabled", False))
                    
                    # --- TRUST VALUE CONVERTER SAFETY check ---
                    trust_token = cfg.get("trust_token", None)
                    if trust_token is not None:
                        decoded_points = self._deobfuscate_trust(trust_token)
                        # Protect memory from corrupt resets or read dropouts
                        if decoded_points > 0 or trust_token == self._obfuscate_trust(0):
                            self.trust_points = decoded_points
                    
                    # --- TRACKER SYNCHRONIZATION ---
                    if hasattr(self, 'var_bubble_light_mode'):
                        self.var_bubble_light_mode.set(cfg.get("bubble_light_mode_enabled", False))
                    else:
                        self.bubble_light_mode_enabled = cfg.get("bubble_light_mode_enabled", False)
                    
                    if hasattr(self, 'var_cooldown_time'): self.var_cooldown_time.set(cfg.get("cooldown_time", 30))
                    if hasattr(self, 'var_disable_snap'): self.var_disable_snap.set(cfg.get("disable_snap_enabled", False))
                    if hasattr(self, 'var_walk_cooldown'): self.var_walk_cooldown.set(cfg.get("walk_cooldown", 300))
                    if hasattr(self, 'var_swap_cooldown'): self.var_swap_cooldown.set(cfg.get("swap_cooldown", 300))
                    if hasattr(self, 'var_afk_cooldown'): self.var_afk_cooldown.set(cfg.get("afk_cooldown", 300))
                    if hasattr(self, 'var_chat_cooldown'): self.var_chat_cooldown.set(cfg.get("chat_cooldown", 30))
                    if hasattr(self, 'var_monitor_cooldown'): self.var_monitor_cooldown.set(cfg.get("monitor_cooldown", 180))
                    
                    saved_moods = cfg.get("mood_states", {})
                    for k, v in saved_moods.items():
                        if hasattr(self, 'mood_states') and k in self.mood_states:
                            self.mood_states[k].set(v)
                    
                    break # Read succeeded perfectly, exit the retry loop safely!
                except (json.JSONDecodeError, PermissionError):
                    time.sleep(0.02) # File was locked or busy, wait 20ms and try again
                except Exception:
                    break

    def save_config_profile(self):
        script_dir = self.get_script_dir()
        config_path = os.path.join(script_dir, "config.json")
        try:
            self.root.update_idletasks()
            cfg = {
                "scale": self.current_scale,
                "costume": self.current_image_filename,
                "pinned": self.is_pinned,
                "click_through": self.is_click_through,
                "flipped": self.is_flipped,
                "opacity": self.current_opacity,
                "chat_enabled": self.chat_enabled,
                "monitor_enabled": self.monitor_enabled,
                "x": self.root.winfo_x(),
                "y": self.root.winfo_y(),
                "home_x": self.home_x,
                "home_y": self.home_y,
                "alarm_time_str": self.alarm_time_str,
                "swapper_enabled": self.var_swapper.get(),
                "patrol_enabled": self.var_patrol.get(),
                "click_irritation_enabled": self.var_irritation.get(),

                "last_login_date": getattr(self, "last_login_date", None),
                "head_shortcut_setting": self.head_shortcut_setting,

                # --- CIPHER EXPORT PROCESS ---
                "trust_token": self._obfuscate_trust(self.trust_points),
                "trust_frozen_enabled": self.var_freeze_trust.get(),
                
                "bubble_light_mode_enabled": self.var_bubble_light_mode.get(),
                "user_name": self.user_name,
                "disable_snap_enabled": self.var_disable_snap.get(),
                "cooldown_time": self.var_cooldown_time.get(),
                "mood_states": {k: v.get() for k, v in self.mood_states.items()}
            }
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=4)
        except Exception as e:
            print("Crash during file write process:", e)

    def open_settings_dashboard(self):
        if hasattr(self, '_dash_win') and self._dash_win.winfo_exists():
            self._dash_win.lift()
            self._dash_win.focus_force()
            return

        self._dash_win = tk.Toplevel(self.root, bg="#1e1e1e")
        self._dash_win.title("Pulchra Config Panel")
        self._dash_win.resizable(False, False)
        self._dash_win.wm_attributes("-topmost", True)

        script_dir = self.get_script_dir()
        icon_path = get_asset_path("pulchra_overlay_icon.ico")
        if os.path.exists(icon_path):
            try:
                self._dash_win.iconbitmap(icon_path)
            except Exception:
                pass

        screen_w = self._dash_win.winfo_screenwidth()
        screen_h = self._dash_win.winfo_screenheight()
        
        # EXTENDED WINDOW BOUNDS: Set height to 610 to eliminate layout crunching entirely
        center_x = (screen_w // 2) - (650 // 2)
        center_y = (screen_h // 2) - (610 // 2)
        self._dash_win.geometry(f"650x610+{center_x}+{center_y}")

        # --- LEFT COLUMN: DIALOGUE MOOD CHECKS ---
        # HEIGHT OPTIMIZED: Lengthened to 550 to let buttons breathe evenly
        mood_frame = tk.LabelFrame(self._dash_win, text=" Dialogue Mood Multi-Select ", bg="#1e1e1e", fg="#e1e4e8", font=("Segoe UI", 9, "bold"), padx=10, pady=10)
        mood_frame.place(x=10, y=10, width=200, height=550)

        for mood_key, var in self.mood_states.items():
            display_label = mood_key.replace("_", " ").title() + " Mode"
            tk.Checkbutton(
                mood_frame, text=display_label, variable=var,
                command=lambda k=mood_key: self.toggle_menu_mood(k),
                bg="#1e1e1e", fg="white", selectcolor="#2d2d2d",
                activebackground="#1e1e1e", activeforeground="white",
                font=("Segoe UI", 9), anchor="w"
            ).pack(fill="x", pady=4)

        tk.Frame(mood_frame, bg="#2d2d2d", height=1).pack(fill="x", pady=12)

        btn_container = tk.Frame(mood_frame, bg="#1e1e1e")
        btn_container.pack(fill="x")
        tk.Button(btn_container, text="All On", command=self.master_mood_all_on, bg="#2d2d2d", fg="white", bd=0, pady=4, font=("Segoe UI", 9)).pack(side="left", expand=True, padx=2)
        tk.Button(btn_container, text="All Off", command=self.master_mood_all_off, bg="#2d2d2d", fg="white", bd=0, pady=4, font=("Segoe UI", 9)).pack(side="right", expand=True, padx=2)

        tk.Frame(mood_frame, bg="#2d2d2d", height=1).pack(fill="x", pady=12)

        tk.Checkbutton(
            mood_frame, text="Light Mode Bubbles", variable=self.var_bubble_light_mode,
            command=self.save_config_profile,
            bg="#1e1e1e", fg="white", selectcolor="#2d2d2d",
            activebackground="#1e1e1e", activeforeground="white",
            font=("Segoe UI", 9, "bold"), anchor="w"
        ).pack(fill="x", pady=4)

        tk.Checkbutton(
            mood_frame, text="Pause Trust Meter", variable=self.var_freeze_trust,
            command=self.save_config_profile,
            bg="#1e1e1e", fg="white", selectcolor="#2d2d2d",
            activebackground="#1e1e1e", activeforeground="white",
            font=("Segoe UI", 9, "bold"), anchor="w"
        ).pack(fill="x", pady=4)

        # 1. Configure Custom Home Anchor Location
        tk.Button(
            mood_frame, text="Configure Custom Anchor", 
            command=self.save_current_as_home_anchor, 
            bg="#2d2d2d", fg="white", bd=0, pady=6, 
            font=("Segoe UI", 9, "bold"), activebackground="#3d3d3d", activeforeground="white"
        ).pack(fill="x", pady=(12, 0))

        # 2. Bind Head Tap Target Shortcut Menu Layout Trigger
        tk.Button(
            mood_frame, text="Bind Head Tap Shortcut...", 
            command=self.open_shortcut_binding_selector_pop, 
            bg="#2d2d2d", fg="#ff9900", bd=0, pady=6, 
            font=("Segoe UI", 9, "bold"), activebackground="#3d3d3d", activeforeground="#ff9900"
        ).pack(fill="x", pady=(10, 0))

        # 3. Reset Defaults Dashboard Option
        tk.Button(
            mood_frame, text="Reset Settings", 
            command=self.reset_dashboard_settings, 
            bg="#2d2d2d", fg="white", bd=0, pady=6, 
            font=("Segoe UI", 9, "bold"), activebackground="#3d3d3d", activeforeground="white"
        ).pack(fill="x", pady=(10, 0))
        # --- CENTER COLUMN UPPER: EXPANDED SYSTEM UTILITIES ---
        # HEIGHT EXTENDED: Set to 255 to align the layout split line
        util_frame = tk.LabelFrame(self._dash_win, text=" System Utilities ", bg="#1e1e1e", fg="#e1e4e8", font=("Segoe UI", 9, "bold"), padx=10, pady=10)
        util_frame.place(x=225, y=10, width=205, height=255)

        tk.Checkbutton(util_frame, text="Toggle Chat Bubbles", variable=self.var_chat, command=self.toggle_chat_bubbles, bg="#1e1e1e", fg="white", selectcolor="#2d2d2d", activebackground="#1e1e1e", activeforeground="white", font=("Segoe UI", 9), anchor="w").pack(fill="x", pady=4)
        tk.Checkbutton(util_frame, text="Auto-Costume Swap", variable=self.var_swapper, command=self.toggle_costume_swapper, bg="#1e1e1e", fg="white", selectcolor="#2d2d2d", activebackground="#1e1e1e", activeforeground="white", font=("Segoe UI", 9), anchor="w").pack(fill="x", pady=4)
        tk.Checkbutton(util_frame, text="Edge Patrol Walks", variable=self.var_patrol, command=self.toggle_patrol_system, bg="#1e1e1e", fg="white", selectcolor="#2d2d2d", activebackground="#1e1e1e", activeforeground="white", font=("Segoe UI", 9), anchor="w").pack(fill="x", pady=4)
        tk.Checkbutton(util_frame, text="Resource Monitor", variable=self.var_monitor, command=self.toggle_resource_monitor, bg="#1e1e1e", fg="white", selectcolor="#2d2d2d", activebackground="#1e1e1e", activeforeground="white", font=("Segoe UI", 9), anchor="w").pack(fill="x", pady=4)
        tk.Checkbutton(util_frame, text="Click Irritation Mode", variable=self.var_irritation, command=self.toggle_click_irritation_system, bg="#1e1e1e", fg="white", selectcolor="#2d2d2d", activebackground="#1e1e1e", activeforeground="white", font=("Segoe UI", 9), anchor="w").pack(fill="x", pady=4)
        tk.Checkbutton(util_frame, text="Disable Edge Snapping", variable=self.var_disable_snap, command=lambda: self.root.after(10, self.save_config_profile), bg="#1e1e1e", fg="white", selectcolor="#2d2d2d", activebackground="#1e1e1e", activeforeground="white", font=("Segoe UI", 9), anchor="w").pack(fill="x", pady=4)

        # --- CENTER COLUMN LOWER: EXPANDED WINDOW LAYOUT & SCALING ---
        # POSITION AND HEIGHT EXTENDED: Shifted to y=275, height increased to 285 to utilize bottom gaps
        layout_frame = tk.LabelFrame(self._dash_win, text=" Window Layout & Scaling ", bg="#1e1e1e", fg="#e1e4e8", font=("Segoe UI", 9, "bold"), padx=10, pady=8)
        layout_frame.place(x=225, y=275, width=205, height=285)

        tk.Checkbutton(layout_frame, text="Toggle Drag Lock", variable=self.var_pinned, command=self.toggle_pin, bg="#1e1e1e", fg="white", selectcolor="#2d2d2d", activebackground="#1e1e1e", activeforeground="white", font=("Segoe UI", 9), anchor="w").pack(fill="x", pady=2)
        tk.Checkbutton(layout_frame, text="Click-Through Mode", variable=self.var_click_through, command=self.toggle_click_through, bg="#1e1e1e", fg="white", selectcolor="#2d2d2d", activebackground="#1e1e1e", activeforeground="white", font=("Segoe UI", 9), anchor="w").pack(fill="x", pady=2)
        
        tk.Label(layout_frame, text="Size Scale Factor:", bg="#1e1e1e", fg="#e1e4e8", font=("Segoe UI", 8)).pack(anchor="w", pady=(8, 0))
        self.slider_scale = tk.Scale(layout_frame, from_=0.5, to=2.0, resolution=0.05, orient="horizontal", bg="#1e1e1e", fg="white", troughcolor="#2d2d2d", activebackground="white", highlightthickness=0, bd=0, command=lambda v: self.change_size(float(v)))
        self.slider_scale.set(self.current_scale)
        self.slider_scale.pack(fill="x", pady=(0, 4))

        tk.Label(layout_frame, text="Opacity Level:", bg="#1e1e1e", fg="#e1e4e8", font=("Segoe UI", 8)).pack(anchor="w", pady=(4, 0))
        self.slider_opacity = tk.Scale(layout_frame, from_=0.25, to=1.0, resolution=0.01, orient="horizontal", bg="#1e1e1e", fg="white", troughcolor="#2d2d2d", activebackground="white", highlightthickness=0, bd=0, command=lambda v: self.change_opacity_live(float(v)))
        self.slider_opacity.set(self.current_opacity)
        self.slider_opacity.pack(fill="x", pady=(0, 8))

        tk.Button(layout_frame, text="Flip Direction (Mirror)", command=self.toggle_flip, bg="#2d2d2d", fg="white", bd=0, pady=5, font=("Segoe UI", 9)).pack(fill="x", pady=(4, 0))
        tk.Button(layout_frame, text="Change Proxy Name...", command=self.prompt_custom_name, bg="#2d2d2d", fg="white", bd=0, pady=8, font=("Segoe UI", 9)).pack(fill="x", pady=(8, 0))    

        # --- RIGHT COLUMN: EXPANDED AUTOMATION INTERVAL COOLDOWNS ---
        # HEIGHT EXTENDED: Set to 550 to align cleanly with the outer panels
        cooldown_frame = tk.LabelFrame(self._dash_win, text=" Automation Intervals (Seconds) ", bg="#1e1e1e", fg="#e1e4e8", font=("Segoe UI", 9, "bold"), padx=10, pady=10)
        cooldown_frame.place(x=440, y=10, width=200, height=550)

        tk.Label(cooldown_frame, text="Chat Frequency:", bg="#1e1e1e", fg="#e1e4e8", font=("Segoe UI", 8)).pack(anchor="w", pady=(4, 0))
        self.sld_chat = tk.Scale(cooldown_frame, from_=5, to=120, resolution=5, orient="horizontal", bg="#1e1e1e", fg="white", troughcolor="#2d2d2d", activebackground="white", highlightthickness=0, bd=0, variable=self.var_chat_cooldown, command=lambda v: self.save_config_profile())
        self.sld_chat.pack(fill="x", pady=(0, 8))

        tk.Label(cooldown_frame, text="Patrol Walk Delay:", bg="#1e1e1e", fg="#e1e4e8", font=("Segoe UI", 8)).pack(anchor="w", pady=(4, 0))
        self.sld_walk = tk.Scale(cooldown_frame, from_=30, to=600, resolution=10, orient="horizontal", bg="#1e1e1e", fg="white", troughcolor="#2d2d2d", activebackground="white", highlightthickness=0, bd=0, variable=self.var_walk_cooldown, command=lambda v: self.save_config_profile())
        self.sld_walk.pack(fill="x", pady=(0, 8))

        tk.Label(cooldown_frame, text="Costume Swap Rate:", bg="#1e1e1e", fg="#e1e4e8", font=("Segoe UI", 8)).pack(anchor="w", pady=(4, 0))
        self.sld_swap = tk.Scale(cooldown_frame, from_=30, to=600, resolution=10, orient="horizontal", bg="#1e1e1e", fg="white", troughcolor="#2d2d2d", activebackground="white", highlightthickness=0, bd=0, variable=self.var_swap_cooldown, command=lambda v: self.save_config_profile())
        self.sld_swap.pack(fill="x", pady=(0, 8))

        tk.Label(cooldown_frame, text="AFK Sleep Sentinel:", bg="#1e1e1e", fg="#e1e4e8", font=("Segoe UI", 8)).pack(anchor="w", pady=(4, 0))
        self.sld_afk = tk.Scale(cooldown_frame, from_=10, to=600, resolution=10, orient="horizontal", bg="#1e1e1e", fg="white", troughcolor="#2d2d2d", activebackground="white", highlightthickness=0, bd=0, variable=self.var_afk_cooldown, command=lambda v: self.save_config_profile())
        self.sld_afk.pack(fill="x", pady=(0, 8))

        tk.Label(cooldown_frame, text="Resource Monitor Alert:", bg="#1e1e1e", fg="#e1e4e8", font=("Segoe UI", 8)).pack(anchor="w", pady=(4, 0))
        self.sld_monitor = tk.Scale(cooldown_frame, from_=10, to=600, resolution=10, orient="horizontal", bg="#1e1e1e", fg="white", troughcolor="#2d2d2d", activebackground="white", highlightthickness=0, bd=0, variable=self.var_monitor_cooldown, command=lambda v: self.save_config_profile())
        self.sld_monitor.pack(fill="x", pady=(0, 8))
        
        guide_text = "Minute Reference Guide:\n60s = 1m | 120s = 2m | 180s = 3m\n240s = 4m | 300s = 5m | 600s = 10m"
        tk.Label(cooldown_frame, text=guide_text, bg="#1e1e1e", fg="#888888", font=("Segoe UI", 8), justify="center").pack(fill="x", pady=(12, 0))



    def toggle_menu_mood(self, mood_key):
        self.save_config_profile()
        if hasattr(self, 'tray_icon'): 
            self.tray_icon.update_menu()

    def master_mood_all_on(self):
        for var in self.mood_states.values():
            var.set(True)
        self.save_config_profile()
        if hasattr(self, 'tray_icon'): self.tray_icon.update_menu()

    def master_mood_all_off(self):
        for var in self.mood_states.values():
            var.set(False)
        self.save_config_profile()
        if hasattr(self, 'tray_icon'): self.tray_icon.update_menu()

    def reset_dashboard_settings(self):
        # Trigger a native overlay confirmation check
        if not messagebox.askyesno("Reset Configuration", "Are you sure you want to restore all settings to their default values?\n\n(Your trust meter state will remain untouched.)", parent=self.root):
            return

        # --- CRITICAL PROTECTION STEP: Lock current trust value in memory ---
        preserved_trust = self.trust_points

        # 1. Reset Mood States
        for k, var in self.mood_states.items():
            var.set(k == "casual")
            
        # 2. Reset System Utilities Variables
        self.var_chat.set(False)
        self.var_swapper.set(True)
        self.var_patrol.set(True)
        self.var_monitor.set(False)
        self.var_irritation.set(True)
        self.var_disable_snap.set(False)
        self.var_bubble_light_mode.set(False)
        
        # 3. Reset Layout Metric Sliders (Sync UI values if dashboard is currently open)
        if hasattr(self, 'slider_scale') and self.slider_scale.winfo_exists(): self.slider_scale.set(1.0)
        if hasattr(self, 'slider_opacity') and self.slider_opacity.winfo_exists(): self.slider_opacity.set(1.0)
        
        # 4. Reset Automation Interval Values
        self.var_chat_cooldown.set(30)
        self.var_walk_cooldown.set(300)
        self.var_swap_cooldown.set(300)
        self.var_afk_cooldown.set(300)
        self.var_monitor_cooldown.set(180)
        
        # 5. Live update engine behaviors to process changes safely
        self.toggle_chat_bubbles()
        self.toggle_costume_swapper()
        self.toggle_patrol_system()
        self.toggle_resource_monitor()
        self.toggle_click_irritation_system()
        self.change_size(1.0)
        self.change_opacity_live(1.0)

        # --- RESTORE AND SYNC STEP ---
        # Force-overwrite any accidental modifications caused by intermediate saving
        self.trust_points = preserved_trust
        self.save_config_profile()
        
        # Force redraw the system tray so all its checkboxes immediately display the new defaults
        if hasattr(self, 'tray_icon'):
            self.tray_icon.update_menu()

    def toggle_tray_mood(self, mood_key):
        self.root.after(0, lambda: [
            self.mood_states[mood_key].set(not self.mood_states[mood_key].get()),
            self.save_config_profile(),
            self.tray_icon.update_menu()
        ])
        
    def set_tray_mood(self, mood_value):
        self.root.after(0, lambda: [
            self.toggle_tray_mood(mood_value) if mood_value in self.mood_states else None
        ])


    def load_external_phrases(self):
        script_dir = self.get_script_dir()
        mood_json_path = os.path.join(script_dir, "pulchra_mood_quotes.json")
        quotes_path = os.path.join(script_dir, "quotes.txt")

        # 1. Standard structural map to safely reference categories if JSON is missing
        self.mood_phrases_fallback = {
            "casual": ["Take it easy. No need to stress over it."],
            "work": ["Promises are cheap out here. Show me some clean results."],
            "coding": ["More syntax blocks? Check your dictionary parameters."],
            "gaming": ["Running game environments? Don't let your framing drop."],
            "relaxed": ["You look way too relaxed. That's how you get blindsided."],
            "focus": ["Head down. Complete the terminal loop."],
            "late_night": ["Still typing at this hour? Your screen glare is blinding my layout."]
        }

        # 2. Check for, create, or read your custom pulchra_mood_quotes.json file
        if not os.path.exists(mood_json_path):
            try:
                # Generates your template holding slots for 40 custom strings per list
                template_pool = {mood: [f"Custom text line placeholder for {mood} mode line {i+1}." for i in range(40)] for mood in self.mood_phrases_fallback.keys()}
                with open(mood_json_path, "w", encoding="utf-8") as f:
                    json.dump(template_pool, f, indent=4)
                self.mood_phrases_fallback = template_pool
            except Exception:
                pass
        else:
            try:
                with open(mood_json_path, "r", encoding="utf-8") as f:
                    self.mood_phrases_fallback = json.load(f)
            except Exception:
                pass

        # 3. Streamlined structural loading sequence
        self.phrases = []
        if hasattr(self, 'mood_phrases_fallback'):
            for lines_list in self.mood_phrases_fallback.values():
                self.phrases.extend(lines_list)
        
        # 4. FIXED: If the custom JSON was just generated, make sure we still use fallback strings
        if not self.phrases or len(self.phrases) <= 7:
            self.phrases = [
                "Take it easy. No need to stress over it.",
                "Surprised? Heh, I knew you'd look up.",
                "Move, will ya? You're blocking my view of the screen.",
                "Too many people get emotional over small details. Don't be one of 'em.",
                "Valuable info always comes with a bit of risk. Just how it goes.",
                "Promises are cheap out here. Show me the results.",
                "If anyone asks, you didn't see me hanging out on your screen. Got it?",
                "This is my turf now. Well, this corner of the desktop, anyway.",
                "Hey! Watch the tail. Touching it is gonna cost ya extra.",
                "Mind your own business. I'm just auditing your desktop layout.",
                "Don't get overly attached to me. This is just a temporary gig.",
                "Focus. Let's get this finished quickly."
            ]

    def load_external_costume_quotes(self):
        script_dir = self.get_script_dir()
        json_path = os.path.join(script_dir, "pulchra_costumes.json")
        
        # Hardcoded internal recovery backup pool
        self.costume_quotes_fallback = {
            "pulchra_overlay_standing.png": [
                "Move, will ya? You're blocking my view of the screen.",
                "What? You think I'm softening up just because we've been idling here?",
                "Focus. Let's get this finished quickly.",
                "Just standing by. Don't make me wait here all day.",
                "This corner of your monitor is mine now. Get used to it."
            ],
            "pulchra_overlay_sitting.png": [
                "Yeah, yeah, I'm sitting down. Don't expect me to start purring like a house pet.",
                "You look way too relaxed. That's how you get blindsided.",
                "Take it easy. No need to stress over it.",
                "Fine, I'll take a quick breather. But don't get lazy."
            ],
            "pulchra_overlay_action_1.png": [
                "Ready for some action when you are... assuming it's actually worth my time.",
                "Let me calculate the risk of whatever task you're running right now.",
                "Promises are cheap out here. Show me the results.",
                "Gotta keep the claws sharp. Typing away isn't the only way to get work done."
            ],
            "pulchra_overlay_action_2.png": [
                "Alright, enough planning. Let's see if your strategy actually holds up when things get messy.",
                "My claws are sharp and I'm losing my patience. Give me something worth dropping into.",
                "Don't just stare at the screen. If we're moving, let's move—time is gear coins.",
                "Let's see if this assignment is actually going to keep me awake. Don't disappoint me."
            ],
            "pulchra_overlay_thinking.png": [
                "Read it once, absorb the data, and move on. Don't overthink it.",
                "Hey, if things go sideways with your code, I'm cutting my losses.",
                "Mind your own business. I'm just auditing your desktop layout.",
                "Let's play a little game. Guess what file I'm looking at right now."
            ],
            "pulchra_overlay_tail.png": [
                "Hey! Watch the tail. Touching it is gonna cost ya extra gear coins.",
                "Seriously? Hands off the tail. I'm trying to concentrate here.",
                "Keep your hands on your keyboard and off of me. Got it?",
                "Is this a distraction tactic? Because it's not working."
                "I'm warning you, I bite."
            ],
            "pulchra_nomask_action.png": [
                "Fine, I'll fight without the mask. Don't let it distract you.",
                "Claws out, eyes on the target. Let's make this quick.",
                "You wanted to see my face? Hope you're ready for the premium rate."
            ],
            "pulchra_nomask_sitting.png": [
                "It's nice to actually breathe without that plate over my face.",
                "What are you staring at? Haven't you ever seen a Thiren take a break?",
                "Don't get used to this. The mask goes back on when we start running real commissions."
            ],
            "pulchra_overlay_casual.png": [
                "What? Never seen a merc off the clock? Don't expect me to run any overtime commissions in these clothes.",
                "No mask, no armor. Just let me sit here and catch up in peace.",
                "I'm off duty right now, Proxy. Go mess with someone else's window.",
                "I'm still keeping tabs on your desktop. Don't slack off.",
                "Don't get too used to this look. The moment a contract drops, my mask goes right back on."
            ],
            "pulchra_overlay_burnt.png": [
                "Ugh... I swear, if Burnice brought her fuel tanks near my corner again, I'm cutting my losses and logging out.",
                "Are you blind? My tail is completely scorched! This is going to cost you serious gear coins next time.",
                "Great. Absolutely perfect. My fur is ruined and you're laughing.",
                "Do NOT laugh. Say one word about the smoke, Proxy, and I'm hiding your cursor inputs for a week.",
                "Clear the workspace and back up your data right now. This place is melting."
            ]
        }
        
        if not os.path.exists(json_path):
            try:
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(self.costume_quotes_fallback, f, indent=4)
                self.costume_quotes = self.costume_quotes_fallback
            except Exception:
                self.costume_quotes = self.costume_quotes_fallback
        else:
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    self.costume_quotes = json.load(f)
            except Exception:
                self.costume_quotes = self.costume_quotes_fallback


    def load_and_scale_image(self, initial_run=False):
        script_dir = self.get_script_dir()
        image_path = get_asset_path(self.current_image_filename)
        
        if not os.path.exists(image_path):
            default_path = get_asset_path("pulchra_overlay_standing.png")
            if os.path.exists(default_path):
                self.current_image_filename = "pulchra_overlay_standing.png"
                image_path = default_path
            else:
                messagebox.showerror("Companion Error", f"Cannot find image file in folder:\n{script_dir}")
                self.quit_application()
                return

        img = Image.open(image_path).convert("RGBA")
        if self.is_flipped:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)

        orig_w, orig_h = img.size
        aspect_ratio = orig_w / orig_h

        base_height = self.target_height
        if self.current_image_filename in [
            "pulchra_overlay_sitting.png", "pulchra_nomask_sitting.png",
            "pulchra_overlay_casual.png", "pulchra_overlay_burnt.png"
        ]:
            base_height = int(self.target_height * 0.9)


        target_h = int(base_height * self.current_scale)
        target_w = int(target_h * aspect_ratio)
        resized_img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)

        # --- FIXED RENDERING LOOP ---
        # Safe modern Pillow sequence unpacking without deprecation alerts
        datas = resized_img.get_flattened_data()
        smooth_data = []

        for px in datas:
            if not isinstance(px, (tuple, list)) or len(px) < 4:
                smooth_data.append(px)
                continue
                
            alpha = px[3] # Extract the 4th item (Alpha) safely
            if alpha < 30: 
                smooth_data.append((255, 0, 255, 0))
            elif alpha < 235:
                smooth_data.append((px[0], px[1], px[2], 255))  
            else:
                smooth_data.append(px)
                
        resized_img.putdata(smooth_data)

        bg_sheet = Image.new("RGBA", resized_img.size, (255, 0, 255, platform_support.image_background_alpha)) 
        bg_sheet.alpha_composite(resized_img)
        self.photo = ImageTk.PhotoImage(bg_sheet)
        self.label.config(image=self.photo)
        self.shape_linux_window(resized_img)
        
        if initial_run:
            if self.saved_x is not None and self.saved_y is not None:
                self.root.geometry(f"{target_w}x{target_h}+{self.saved_x}+{self.saved_y}")
            else:
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                x_offset = screen_width - target_w - 30   
                y_offset = screen_height - target_h - 70  
                self.root.geometry(f"{target_w}x{target_h}+{x_offset}+{y_offset}")
            self.root.attributes("-alpha", self.current_opacity)
        else:
            old_w, old_h = self.root.winfo_width(), self.root.winfo_height()
            current_x = self.root.winfo_x() + (old_w - target_w) // 2
            current_y = self.root.winfo_y() + (old_h - target_h)
            self.root.geometry(f"{target_w}x{target_h}+{current_x}+{current_y}")
            self.save_config_profile()
            
        if self.bubble_window and self.bubble_window.winfo_exists():
            self.update_bubble_position()


    def change_costume(self, filename):
        self.current_image_filename = filename
        self.save_config_profile()
        self.load_and_scale_image(initial_run=False)
        if hasattr(self, 'tray_icon'):
            try:
                self.tray_icon.update_menu()
            except Exception:
                pass

    def create_context_menu(self):
        self.menu = tk.Menu(self.root, tearoff=0, bg="#1e1e1e", fg="white", activebackground="#2d2d2d", selectcolor="white")
        
        # --- SELECT COSTUME SUB-MENU ---
        costume_menu = tk.Menu(self.menu, tearoff=0, bg="#1e1e1e", fg="white")
        costume_menu.add_command(label="Standing", command=lambda: self.change_costume("pulchra_overlay_standing.png"))
        costume_menu.add_command(label="Sitting", command=lambda: self.change_costume("pulchra_overlay_sitting.png"))
        costume_menu.add_command(label="Casual", command=lambda: self.change_costume("pulchra_overlay_casual.png"))
        costume_menu.add_command(label="Action 1", command=lambda: self.change_costume("pulchra_overlay_action_1.png"))
        costume_menu.add_command(label="Action 2", command=lambda: self.change_costume("pulchra_overlay_action_2.png"))
        costume_menu.add_command(label="No mask Action", command=lambda: self.change_costume("pulchra_nomask_action.png"))
        costume_menu.add_command(label="No mask Sitting", command=lambda: self.change_costume("pulchra_nomask_sitting.png"))
        costume_menu.add_command(label="Petting tail", command=lambda: self.change_costume("pulchra_overlay_tail.png"))
        costume_menu.add_command(label="Thinking", command=lambda: self.change_costume("pulchra_overlay_thinking.png"))
        costume_menu.add_command(label="Burnt", command=lambda: self.change_costume("pulchra_overlay_burnt.png"))
        self.menu.add_cascade(label="Select Costume", menu=costume_menu)
        self.menu.add_separator()

        # --- MASTER CONFIGURATION TRIGGER ---
        self.menu.add_command(label="Open Settings Dashboard...", command=self.open_settings_dashboard)
        self.menu.add_separator()

        # --- QUICK CLICKS & INTEL ---
        self.menu.add_command(label="Get Intel", command=self.force_chat_bubble)
        self.menu.add_command(label="System Pulse Check", command=self.trigger_pulse_check)
        
        timer_menu = tk.Menu(self.menu, tearoff=0, bg="#1e1e1e", fg="white")
        timer_menu.add_command(label="5 Minute Break", command=lambda: self.start_commission_timer(5))
        timer_menu.add_command(label="25 Minute Work", command=lambda: self.start_commission_timer(25))
        timer_menu.add_command(label="1 Hour Grind", command=lambda: self.start_commission_timer(60))
        timer_menu.add_separator()
        timer_menu.add_command(label="Set Custom Timer...", command=self.prompt_custom_timer)
        self.menu.add_cascade(label="Start Contract Timer", menu=timer_menu)

        alarm_menu = tk.Menu(self.menu, tearoff=0, bg="#1e1e1e", fg="white")
        alarm_menu.add_command(label="Set Alarm...", command=self.prompt_custom_alarm)
        alarm_menu.add_command(label="Clear Active Alarm", command=self.clear_active_alarm)
        self.menu.add_cascade(label="Alarm Options", menu=alarm_menu)
        self.menu.add_separator()

        # --- NAVIGATION LAYOUT UTILITIES ---
        anchor_menu = tk.Menu(self.menu, tearoff=0, bg="#1e1e1e", fg="white")
        anchor_menu.add_command(label="Top Left Corner", command=lambda: self.snap_to_screen_node("top_left"))
        anchor_menu.add_command(label="Top Center Edge", command=lambda: self.snap_to_screen_node("top_center"))
        anchor_menu.add_command(label="Top Right Corner", command=lambda: self.snap_to_screen_node("top_right"))
        anchor_menu.add_separator()
        anchor_menu.add_command(label="Middle Left Edge", command=lambda: self.snap_to_screen_node("middle_left"))
        anchor_menu.add_command(label="Middle Right Edge", command=lambda: self.snap_to_screen_node("middle_right"))
        anchor_menu.add_separator()
        anchor_menu.add_command(label="Bottom Left Corner", command=lambda: self.snap_to_screen_node("bottom_left"))
        anchor_menu.add_command(label="Bottom Center Edge", command=lambda: self.snap_to_screen_node("bottom_center"))
        anchor_menu.add_command(label="Bottom Right Anchor", command=lambda: self.snap_to_screen_node("bottom_right"))
        self.menu.add_cascade(label="Snap to Node", menu=anchor_menu)
        
        self.menu.add_command(label="Send to Bottom Right", command=lambda: self.snap_to_screen_node("bottom_right"))
        self.menu.add_command(label="Snap to Nearest Node", command=self.snap_to_closest_node)

        walk_menu = tk.Menu(self.menu, tearoff=0, bg="#1e1e1e", fg="white")
        walk_menu.add_command(label="Top Left Corner", command=lambda: self.route_perimeter_walk("top_left"))
        walk_menu.add_command(label="Top Center Edge", command=lambda: self.route_perimeter_walk("top_center"))
        walk_menu.add_command(label="Top Right Corner", command=lambda: self.route_perimeter_walk("top_right"))
        walk_menu.add_separator()
        walk_menu.add_command(label="Middle Left Edge", command=lambda: self.route_perimeter_walk("middle_left"))
        walk_menu.add_command(label="Middle Right Edge", command=lambda: self.route_perimeter_walk("middle_right"))
        walk_menu.add_separator()
        walk_menu.add_command(label="Bottom Left Corner", command=lambda: self.route_perimeter_walk("bottom_left"))
        walk_menu.add_command(label="Bottom Center Edge", command=lambda: self.route_perimeter_walk("bottom_center"))
        walk_menu.add_command(label="Bottom Right Anchor", command=lambda: self.route_perimeter_walk("bottom_right"))
        self.menu.add_cascade(label="Walk to Node", menu=walk_menu)
        self.menu.add_command(label="Go to Home Anchor", command=self.go_to_home_anchor)


        self.menu.add_command(label="DVD Bouncing Mode", command=self.toggle_dvd_mode)
        self.menu.add_command(label="Open Folder Path", command=self.open_folder)
        self.menu.add_command(label="Cancel Active Patrol", command=self.cancel_active_walk)
        self.menu.add_separator()
        self.menu.add_command(label="About / Credits", command=self.show_credits)
        self.menu.add_command(label="Close Companion (Esc)", command=self.quit_application)

    def change_size(self, scale_factor):
        self.current_scale = scale_factor
        self.root.after(0, self.load_and_scale_image)

    def change_opacity_live(self, opacity_value):
        self.current_opacity = opacity_value
        self.root.attributes("-alpha", opacity_value)
        if self.bubble_window and self.bubble_window.winfo_exists():
            self.bubble_window.attributes("-alpha", opacity_value)

    def toggle_pin(self):
        self.is_pinned = self.var_pinned.get()
        self.save_config_profile()
        if hasattr(self, 'tray_icon'): self.root.after(0, self.tray_icon.update_menu)

    def toggle_flip(self):
        self.is_flipped = not self.is_flipped
        self.root.after(0, self.load_and_scale_image)

    def reset_position(self):
        self.saved_x, self.saved_y = None, None
        self.root.after(0, lambda: self.load_and_scale_image(initial_run=True))

    def open_folder(self):
        platform_support.open_folder(self.get_script_dir())

    def toggle_click_through(self):
        self.is_click_through = self.var_click_through.get()
        self.root.after(0, self.apply_click_through)
        self.save_config_profile()
        if hasattr(self, 'tray_icon'): self.root.after(0, self.tray_icon.update_menu)

    def apply_click_through(self):
        self.is_click_through = platform_support.set_click_through(self.root, self.is_click_through)
        self.var_click_through.set(self.is_click_through)
        if self.is_click_through:
            self.close_chat_bubble()
        self.save_config_profile()

    def show_context_menu(self, event):
        if not self.is_click_through:
            
            self.menu.post(event.x_root, event.y_root)
            self.menu.focus_set()
            self.menu.bind("<FocusOut>", lambda e: self.menu.unpost())

    def check_menu_focus(self):
        focused = self.root.focus_get()
        if focused != self.menu and focused != self.root:
            self.menu.unpost()


            # Keeps the UI checkmark synced when right-clicking
            # Synchronize graphical checkbox state


    def start_drag(self, event):
        if not self.is_click_through:
            now = time.time()
            self.drag_start_time = now
            self.last_drag_time = now
            self.last_x = self.root.winfo_x()
            self.last_y = self.root.winfo_y()
            self.velocity_x = 0
            self.velocity_y = 0
            
            if hasattr(self, "_walk_pool") or getattr(self, "_active_glide_id", None) is not None:
                return

            self.drag_data_x, self.drag_data_y = event.x, event.y

            if hasattr(self, '_dash_win') and self._dash_win.winfo_exists():
                return

            win_w = self.root.winfo_width()
            win_h = self.root.winfo_height()
            if win_w <= 0 or win_h <= 0:
                return

            norm_x = event.x / win_w
            norm_y = event.y / win_h

            if self.is_flipped:
                norm_x = 1.0 - norm_x

            fallback_box = ((0.35, 0.05, 0.65, 0.25), (0.20, 0.60, 0.80, 0.95))
            
            if hasattr(self, 'costume_click_zones') and self.current_image_filename in self.costume_click_zones:
                head_box, tail_box = self.costume_click_zones[self.current_image_filename]
            else:
                head_box, tail_box = fallback_box
                
            hx1, hy1, hx2, hy2 = head_box
            tx1, ty1, tx2, ty2 = tail_box

            # A. HEAD ZONE SHORTCUT
            if hx1 <= norm_x <= hx2 and hy1 <= norm_y <= hy2:
                self.execute_head_shortcut_toggle()
                return

            # B. TAIL IRRITATION TICK
            elif tx1 <= norm_x <= tx2 and ty1 <= norm_y <= ty2:
                self.process_tail_irritation_tick(now)
                return

            # C. BACKUP CONVERSATION FALLBACK
            active_quotes = None
            if hasattr(self, 'costume_quotes') and self.current_image_filename in self.costume_quotes:
                active_quotes = self.costume_quotes[self.current_image_filename]
            elif hasattr(self, 'costume_quotes_fallback') and self.current_image_filename in self.costume_quotes_fallback:
                active_quotes = self.costume_quotes_fallback[self.current_image_filename]
                
            if not active_quotes:
                active_quotes = self.phrases if hasattr(self, 'phrases') and self.phrases else ["..."]
                
            self.trigger_chat_bubble(forced_text=random.choice(active_quotes))

    def process_tail_irritation_tick(self, now):
        if self.click_irritation_enabled:
            if now - self.last_click_timestamp > 15.0:
                self.click_streak_count = 0
            
            self.click_streak_count += 1
            self.last_click_timestamp = now

            pool_mild = [
                "Hey! Watch the tail. Touching it is gonna cost ya extra.",
                "Seriously? Hands off the tail. I'm trying to concentrate here.",
                "Keep your hands on your keyboard and off of me. Got it?",
                "Is this a distraction tactic? Because it's not working.",
                "Mind your pointer layout. Poking my tail won't clear your syntax errors."
            ]
            pool_mad = [
                "Seriously? That's getting old fast. Cut it out.",
                "My claws are sharp and I am rapidly running out of patience.",
                "Do I look like a toy to you? Go tap on a different window parameter.",
                "I'm warning you, I bite. Keep that cursor clear of my tail.",
                "That tail fur takes ages to brush out. Stop messing with it."
            ]
            pool_furious = [
                "Alright, that is it! I am logging out of this partition entirely!",
                "Ugh, absolutely insufferable! Find another companion to annoy!",
                "Contract suspended. I am getting out of your mouse tracking zone!",
                "Nope. Done. Figure out your directory errors by yourself!",
                "You want to play games? Fine, see if you can click me now!"
            ]

            if self.click_streak_count >= 7:
                msg = random.choice(pool_furious)
                if hasattr(self, 'var_freeze_trust') and not self.var_freeze_trust.get():
                    if hasattr(self, 'trust_points'):
                        self.trust_points = max(0, self.trust_points - 5)
                
                self.trigger_chat_bubble(forced_text=msg)
                self.change_opacity_live(0.0)
                self.close_chat_bubble()
                
                corners = ["top_left", "top_right", "bottom_left", "bottom_right"]
                self.snap_to_screen_node(random.choice(corners))
                
                self.click_streak_count = 0
                self.change_costume(self._pre_irritation_costume)
                self.root.after(2000, lambda: self.change_opacity_live(1.0))
                return

            if self.click_streak_count >= 4:
                active_quote = random.choice(pool_mad)
                if self.current_image_filename != "pulchra_overlay_thinking.png":
                    self._pre_irritation_costume = self.current_image_filename
                if random.random() < 0.40:
                    self.change_costume("pulchra_overlay_thinking.png")
            else:
                active_quote = random.choice(pool_mild)
                if self.current_image_filename != "pulchra_overlay_thinking.png":
                    self._pre_irritation_costume = self.current_image_filename

            self.trigger_chat_bubble(forced_text=active_quote)

    def execute_head_shortcut_toggle(self):
        setting = self.head_shortcut_setting
        
        if setting == "pulse":
            # Instantly run the resource diagnostics scan function
            self.trigger_pulse_check()
            return
            
        elif setting == "chat":
            self.var_chat.set(not self.var_chat.get())
            self.toggle_chat_bubbles()
            status = "ENABLED" if self.chat_enabled else "DISABLED"
            msg = f"Head Shortcut: Chat Popups are now {status}."
            
        elif setting == "swapper":
            self.var_swapper.set(not self.var_swapper.get())
            self.toggle_costume_swapper()
            status = "ENABLED" if self.var_swapper.get() else "DISABLED"
            msg = f"Head Shortcut: Auto-Costume Swap is now {status}."
            
        elif setting == "patrol":
            self.var_patrol.set(not self.var_patrol.get())
            self.toggle_patrol_system()
            status = "ENABLED" if self.var_patrol.get() else "DISABLED"
            msg = f"Head Shortcut: Edge Patrol Walks are now {status}."
            
        elif setting == "monitor":
            self.var_monitor.set(not self.var_monitor.get())
            self.toggle_resource_monitor()
            status = "ENABLED" if self.monitor_enabled else "DISABLED"
            msg = f"Head Shortcut: Resource Monitor is now {status}."
            
        elif setting == "irritation":
            self.var_irritation.set(not self.var_irritation.get())
            self.toggle_click_irritation_system()
            status = "ENABLED" if self.click_irritation_enabled else "DISABLED"
            msg = f"Head Shortcut: Click Irritation Mode is now {status}."
            
        elif setting == "snap":
            self.var_disable_snap.set(not self.var_disable_snap.get())
            self.save_config_profile()
            if hasattr(self, 'tray_icon'): 
                self.tray_icon.update_menu()
            status = "DISABLED" if self.var_disable_snap.get() else "ENABLED"
            msg = f"Head Shortcut: Window Edge Snapping is now {status}."
        else:
            msg = "Head Shortcut triggered, but no target profile was bound."

        self.trigger_chat_bubble(forced_text=msg)


    def drag_window(self, event):
        if not self.is_pinned and not self.is_click_through and getattr(self, 'drag_data_x', None) is not None:
            now = time.time()
            dt = now - self.last_drag_time if (now - self.last_drag_time) > 0 else 0.001
            
            delta_x = event.x - self.drag_data_x
            delta_y = event.y - self.drag_data_y
            current_x = self.root.winfo_x()
            current_y = self.root.winfo_y()
            new_x = current_x + delta_x
            new_y = current_y + delta_y
            
            self.velocity_x = (new_x - self.last_x) / dt
            self.velocity_y = (new_y - self.last_y) / dt
            
            self.last_x = new_x
            self.last_y = new_y
            self.last_drag_time = now
            
            # --- MODIFIED SNAPPING BOUNDS HOOK ---
            if not self.var_disable_snap.get():
                screen_w = self.root.winfo_screenwidth()
                screen_h = self.root.winfo_screenheight()
                win_w = self.root.winfo_width()
                win_h = self.root.winfo_height()
                
                snap_threshold = 45
                
                if new_x < snap_threshold: 
                    new_x = 0
                elif (screen_w - (new_x + win_w)) < snap_threshold: 
                    new_x = screen_w - win_w
                    
                if new_y < snap_threshold: 
                    new_y = 0
                elif (screen_h - (new_y + win_h)) < snap_threshold: 
                    new_y = screen_h - win_h
            
            self.root.geometry(f"+{new_x}+{new_y}")
            if self.bubble_window and self.bubble_window.winfo_exists(): 
                self.update_bubble_position()

    def end_drag_save(self, event):
        if not self.is_pinned and not self.is_click_through:
            self.save_config_profile()
            
            speed = (self.velocity_x**2 + self.velocity_y**2)**0.5
            if speed > 1500:
                collision_quotes = [
                    "Whoa! Watch where you're flinging me, will ya?",
                    "Hey! Do I look like a toy you can just toss across the screen?",
                    "Ugh, slow down. You're gonna make me dizzy with that dragging.",
                    "Keep that up and I'm blocking mouse inputs entirely. Be gentle.",
                    "Ouch... a little warning next time you decide to throw me around?"
                ]
                
                self.trigger_chat_bubble(forced_text=random.choice(collision_quotes))
                self.run_window_shake_loop(intensity=8, steps=6)

    def run_window_shake_loop(self, intensity, steps):
        if steps > 0 and self.root.winfo_exists():
            dx = random.choice([-intensity, intensity])
            dy = random.choice([-intensity, intensity])
            cx = self.root.winfo_x()
            cy = self.root.winfo_y()
            self.root.geometry(f"+{cx + dx}+{cy + dy}")
            if self.bubble_window and self.bubble_window.winfo_exists():
                self.update_bubble_position()
            self.root.after(40, lambda: self.run_window_shake_loop(max(1, intensity - 1), steps - 1))



    def prompt_custom_timer(self):
        m = simpledialog.askinteger("New Contract", "Minutes:", parent=self.root, minvalue=1, maxvalue=1440)
        if m: self.start_commission_timer(m)

    def start_commission_timer(self, minutes):
        if self.timer_loop_id: self.root.after_cancel(self.timer_loop_id)
        self.timer_seconds_left = minutes * 60
        self.run_timer_countdown()

    def run_timer_countdown(self):
        if self.timer_seconds_left > 0:
            self.timer_seconds_left -= 1
            self.timer_loop_id = self.root.after(1000, self.run_timer_countdown)
        else:
            self.timer_loop_id = None
            
            # --- AWARD REWARD FOR CONTRACT COMPLETION ---
            if hasattr(self, 'var_freeze_trust') and not self.var_freeze_trust.get():
                if hasattr(self, 'trust_points'):
                    self.trust_points = min(200, self.trust_points + 10)  # Max cap at 200 points
                    self.save_config_profile()
                    
            self.trigger_persistent_timer_popup()


    def toggle_resource_monitor(self):
        if hasattr(self, 'menu') and self.menu.winfo_exists(): self.monitor_enabled = self.var_monitor.get()
        else: self.monitor_enabled = not self.monitor_enabled
        self.save_config_profile()
        if self.monitor_enabled:
            if psutil is None:
                messagebox.showwarning("Missing Library", "Run 'pip install psutil' in terminal.")
                self.monitor_enabled, self.var_monitor = False, tk.BooleanVar(value=False)
            else: self.run_resource_check()
        else:
            if self.monitor_loop_id: self.root.after_cancel(self.monitor_loop_id)
            self.monitor_loop_id = None
        if hasattr(self, 'tray_icon'): self.root.after(0, self.tray_icon.update_menu)

    def run_resource_check(self):
        if not self.monitor_enabled or self.is_click_through or psutil is None: return
        now = time.time()
        
        lockout = self.var_monitor_cooldown.get()
        
        if psutil.cpu_percent() > 85.0 and (now - self.last_cpu_alert_time) > lockout: # <-- Changed 180 to lockout
            self.last_cpu_alert_time = now
            self.trigger_chat_bubble(forced_text="Processor redlining. Heavy pipeline, or a system tantrum?")
            return
        if psutil.virtual_memory().percent > 85.0 and (now - self.last_ram_alert_time) > lockout: # <-- Changed 180 to lockout
            self.last_ram_alert_time = now
            self.trigger_chat_bubble(forced_text="Eating up memory bandwidth. Close some tabs before we crash.")
            return
        b = psutil.sensors_battery()
        if b and b.percent < 50 and not b.power_plugged and (now - self.last_battery_alert_time) > lockout: # <-- Changed 180 to lockout
            self.last_battery_alert_time = now
            self.trigger_chat_bubble(forced_text="Power supply low. Plug it in or this workstation turns into a paperweight.")
            return
        self.monitor_loop_id = self.root.after(10000, self.run_resource_check)


    def start_clipboard_monitor_loop(self):
        if self.is_click_through:
            self._clip_loop_id = self.root.after(4000, self.start_clipboard_monitor_loop)
            return

        try:
            raw_clip = self.root.clipboard_get()
            if len(raw_clip) > 4000:
                current_clip = raw_clip[:4000].strip()
            else:
                current_clip = raw_clip.strip()

            if not hasattr(self, "_last_tracked_clipboard"):
                self._last_tracked_clipboard = current_clip

            if current_clip and current_clip != self._last_tracked_clipboard:
                self._last_tracked_clipboard = current_clip
                lower_clip = current_clip.lower()

                reactions = {
                    "url": [
                        "A web link? Let's hope that domain doesn't host malicious redirect scripts.",
                        "Navigating to a new node? Keep your proxy filters up out there.",
                        "Link copied. Don't go wasting gear coins on sketchy data boards."
                    ],
                    "code": [
                        "More raw syntax blocks? My eyes are starting to blur just looking at your clipboard.",
                        "Copy-pasting lines again? Make sure you actually audit the logic before running it.",
                        "That looks like a heavy script snippet. Optimization pass required."
                    ],
                    "path": [
                        "An absolute directory path. Auditing the file structure now...",
                        "Mapping out a new folder node? Don't leave your workspace cluttered."
                    ],
                    "general": [
                        "Data logged to system clipboard. Let's make sure it's actually useful intel.",
                        "Copy operation detected. Scraping data or just moving text around?",
                        "Clipboard cache updated. Keep your files organized, Proxy."
                    ]
                }

                if lower_clip.startswith(("http://", "https://", "www.")):
                    msg = random.choice(reactions["url"])
                elif any(c in current_clip for c in ["def ", "function", "void ", "import ", "const ", "class "]) or len(current_clip.split('\n')) > 3:
                    msg = random.choice(reactions["code"])
                elif "\\" in current_clip or (lower_clip.startswith("/") and len(current_clip) > 5):
                    msg = random.choice(reactions["path"])
                else:
                    msg = random.choice(reactions["general"])

                if random.random() < 0.25:
                    self.change_costume("pulchra_overlay_thinking.png")
                
                self.trigger_chat_bubble(forced_text=msg)
        except Exception:
            pass  # Safely absorb Windows clipboard lockouts
        finally:
            # --- CRITICAL FIX: Loop survival is completely guaranteed here ---
            self._clip_loop_id = self.root.after(4000, self.start_clipboard_monitor_loop)

    def toggle_chat_bubbles(self):
        # Force a hard sync on the control variables to ensure thread safety
        if hasattr(self, 'menu') and self.menu.winfo_exists(): 
            self.chat_enabled = self.var_chat.get()
        else: 
            self.chat_enabled = not self.chat_enabled
            self.var_chat.set(self.chat_enabled)
            
        self.save_config_profile()
        
        # Explicitly kill and reset any active timer handle to prevent ghost loops
        if getattr(self, "chat_timer_id", None) is not None:
            try:
                self.root.after_cancel(self.chat_timer_id)
            except Exception:
                pass
            self.chat_timer_id = None
            
        if self.chat_enabled:
            self.load_external_phrases()
            self.trigger_chat_bubble()
        else:
            self.close_chat_bubble()
            
        if hasattr(self, 'tray_icon'): 
            self.root.after(0, self.tray_icon.update_menu)

    def force_chat_bubble(self):
        if self.is_click_through: 
            return

        # --- INTERACTION APPRECIATION GAIN ---
        if hasattr(self, 'var_freeze_trust') and not self.var_freeze_trust.get():
            if hasattr(self, 'trust_points'):
                self.trust_points = min(200, self.trust_points + 3)
                self.save_config_profile()

        self.load_external_phrases()
        
        # Fully un-schedule the active loop chain before jumping the line
        if getattr(self, "chat_timer_id", None) is not None:
            try:
                self.root.after_cancel(self.chat_timer_id)
            except Exception:
                pass
            self.chat_timer_id = None
            
        self.trigger_chat_bubble()

    def trigger_chat_bubble(self, forced_text=None):
        if self.is_click_through: 
            return
            
        self.close_chat_bubble()
        
        if getattr(self, "chat_timer_id", None) is not None:
            try:
                self.root.after_cancel(self.chat_timer_id)
            except Exception:
                pass
            self.chat_timer_id = None

        self.bubble_window = tk.Toplevel(self.root)
        self.bubble_window.overrideredirect(True)
        self.bubble_window.wm_attributes("-topmost", True)
        self.bubble_window.attributes("-alpha", self.current_opacity)
        try: 
            self.bubble_window.wm_attributes("-transparentcolor", "#FF00FF")
        except Exception: 
            pass
        configure_transparency(self.bubble_window)
        
        if forced_text:
            msg = forced_text
        else:
            has_fallbacks = hasattr(self, 'mood_phrases_fallback')
            combined_pool = []
            tier = self.get_trust_tier_label()
            
            if has_fallbacks:
                for mood_key, var in self.mood_states.items():
                    if var.get() and mood_key in self.mood_phrases_fallback:
                        mood_data = self.mood_phrases_fallback[mood_key]
                        if isinstance(mood_data, dict):
                            combined_pool.extend(mood_data.get("low", []))
                            
                            if self.trust_points >= 40:
                                combined_pool.extend(mood_data.get("neutral", []))
                                
                            if self.trust_points >= 150:
                                combined_pool.extend(mood_data.get("high", []))
                        elif isinstance(mood_data, list):
                            combined_pool.extend(mood_data)
                        
            # Only pick from active checkmarks if a selection exists
            if combined_pool:
                msg = random.choice(combined_pool)
            else:
                msg = random.choice(self.phrases)

        try:
            msg = msg.format(name=self.user_name)
        except Exception:
            pass

        px, py, mw = 10, 6, 150
        lbl = tk.Label(self.bubble_window, text=msg, font=("Segoe UI", 9), fg="#e1e4e8", wraplength=mw)
        lbl.update_idletasks()
        tw, th = lbl.winfo_reqwidth(), lbl.winfo_reqheight()
        lbl.destroy()
        
        bw, bh, th_h = tw + (px * 2), th + (py * 2), 8  
        canvas = tk.Canvas(self.bubble_window, width=bw, height=bh + th_h, bg="#FF00FF", bd=0, highlightthickness=0)
        canvas.pack()

        if self.var_bubble_light_mode.get():
            bubble_bg = "#f0f0f0"
            bubble_fg = "#222222"
        else:
            bubble_bg = "#24292e"
            bubble_fg = "#e1e4e8"

        r = 8  
        canvas.create_oval(0, 0, r*2, r*2, fill=bubble_bg, outline=bubble_bg)
        canvas.create_oval(bw - r*2, 0, bw, r*2, fill=bubble_bg, outline=bubble_bg)
        canvas.create_oval(0, bh - r*2, r*2, bh, fill=bubble_bg, outline=bubble_bg)
        canvas.create_oval(bw - r*2, bh - r*2, bw, bh, fill=bubble_bg, outline=bubble_bg)
        canvas.create_rectangle(r, 0, bw - r, bh, fill=bubble_bg, outline=bubble_bg)
        canvas.create_rectangle(0, r, bw, bh - r, fill=bubble_bg, outline=bubble_bg)
        tw_half, tx = 6, bw // 2
        
        canvas.create_polygon(tx - tw_half, bh - 1, tx + tw_half, bh - 1, tx, bh + th_h, fill=bubble_bg, outline=bubble_bg)
        canvas.create_text(bw // 2, bh // 2, text=msg, fill=bubble_fg, font=("Segoe UI", 9), width=mw, justify="center")

        self.update_bubble_position()
        
        if self.click_irritation_enabled and self.current_image_filename == "pulchra_overlay_thinking.png":
            def safe_costume_revert():
                if time.time() - self.last_click_timestamp >= 15.0 and self.current_image_filename == "pulchra_overlay_thinking.png":
                    self.current_image_filename = self._pre_irritation_costume
                    self.load_and_scale_image(initial_run=False)
                    if hasattr(self, 'tray_icon'):
                        try: self.tray_icon.update_menu()
                        except Exception: pass
            self.root.after(15000, safe_costume_revert)

        self.auto_hide_id = self.root.after(7000, self.close_chat_bubble)
        
        if self.chat_enabled and getattr(self, "chat_timer_id", None) is None:
            self.chat_timer_id = self.root.after(self.var_chat_cooldown.get() * 1000, self.trigger_chat_bubble)

    def update_bubble_position(self):
        if self.bubble_window and self.bubble_window.winfo_exists():
            self.bubble_window.update_idletasks()
            
            b_width = self.bubble_window.winfo_reqwidth()
            b_height = self.bubble_window.winfo_reqheight()
            
            bx = self.root.winfo_x() + (self.root.winfo_width() // 2) - (b_width // 2)
            by = self.root.winfo_y() - b_height - 4
            self.bubble_window.geometry(f"{b_width}x{b_height}+{bx}+{by}")

    def close_chat_bubble(self):
        if getattr(self, "auto_hide_id", None) is not None:
            try:
                self.root.after_cancel(self.auto_hide_id)
            except Exception:
                pass
            self.auto_hide_id = None
            
        if self.bubble_window:
            try: 
                self.bubble_window.destroy()
            except Exception: 
                pass
            self.bubble_window = None

    def setup_system_tray(self):
        platform_support.setup_tray(self)
        
    def safe_tray_toggle_chat(self):
        self.root.after(0, lambda: [
            self.var_chat.set(not self.chat_enabled),
            self.toggle_chat_bubbles(),
            self.tray_icon.update_menu()  
        ])

    def safe_tray_toggle_monitor(self):
        self.root.after(0, lambda: [
            self.var_monitor.set(not self.monitor_enabled),
            self.toggle_resource_monitor(),
            self.tray_icon.update_menu() 
        ])

    def safe_tray_toggle_swapper(self):
        self.root.after(0, lambda: [
            self.var_swapper.set(not getattr(self, '_swapper_state', True)),
            self.toggle_costume_swapper(),
            self.tray_icon.update_menu() 
        ])

    def safe_tray_toggle_patrol(self):
        self.root.after(0, lambda: [
            self.var_patrol.set(not self.var_patrol.get()),
            self.toggle_patrol_system(),
            self.tray_icon.update_menu() 
        ])


    def safe_tray_toggle_pin(self):
        self.root.after(0, lambda: [
            self.var_pinned.set(not self.is_pinned),
            self.toggle_pin()
        ])

    def safe_tray_toggle_click(self):
        self.root.after(0, lambda: [
            self.var_click_through.set(not self.is_click_through),
            self.toggle_click_through()
        ])

    def safe_tray_toggle_snap(self):
        self.root.after(0, lambda: [
            self.var_disable_snap.set(not self.var_disable_snap.get()),
            self.save_config_profile(),
            self.tray_icon.update_menu()
        ])

    def safe_tray_toggle_freeze_trust(self):
        self.root.after(0, lambda: [
            self.var_freeze_trust.set(not self.var_freeze_trust.get()),
            self.save_config_profile(),
            self.tray_icon.update_menu()
        ])

    def safe_tray_call_reset(self):
        self.root.after(0, self.reset_dashboard_settings)


    def start_random_walk_loop(self):
        if hasattr(self, '_walk_loop_id') and self._walk_loop_id:
            self.root.after_cancel(self._walk_loop_id)
            self._walk_loop_id = None

        if self.var_patrol.get() and not self.is_pinned and not self.is_click_through:
            nodes = ["top_left", "top_center", "top_right", "middle_left", "middle_right", "bottom_left", "bottom_center", "bottom_right"]
            target_node = random.choice(nodes)
            self.route_perimeter_walk(target_node)
            
        if self.var_patrol.get():
            cooldown_ms = self.var_walk_cooldown.get() * 1000
            self._walk_loop_id = self.root.after(cooldown_ms, self.start_random_walk_loop)


    def toggle_patrol_system(self):
        self._patrol_state = self.var_patrol.get()        
        # Update menu across threads
        if hasattr(self, 'tray_icon'):
            self.root.after(0, self.tray_icon.update_menu)
        # Clear loop if turned off
        if not self.var_patrol.get() and hasattr(self, '_walk_loop_id') and self._walk_loop_id:
            self.root.after_cancel(self._walk_loop_id)
            self._walk_loop_id = None
        elif self.var_patrol.get():
            self.start_random_walk_loop()
        self.save_config_profile()

    def route_perimeter_walk(self, target_node):
        # FIX: Always capture and save her active costume BEFORE she starts walking
        # This covers both automated random walks and manual menu commands!
        if hasattr(self, '_active_glide_id') and self._active_glide_id:
            self.root.after_cancel(self._active_glide_id)
            self._active_glide_id = None
            
        if hasattr(self, "_walk_pool"): 
            delattr(self, "_walk_pool")
            
        if self.current_image_filename not in [
            "pulchra_walking_rightmid1.png", "pulchra_walking_rightleft.png", 
            "pulchra_walking_rightmid2.png", "pulchra_walking_rightright.png",
            "pulchra_walking_leftmid1.png", "pulchra_walking_leftleft.png", 
            "pulchra_walking_leftmid2.png", "pulchra_walking_leftright.png",
            "pulchra_walking_upmid1.png", "pulchra_walking_upleft.png", 
            "pulchra_walking_upmid2.png", "pulchra_walking_upright.png",
            "pulchra_walking_downmid1.png", "pulchra_walking_downleft.png", 
            "pulchra_walking_downmid2.png", "pulchra_walking_downright.png"
        ]:
            self._pre_walk_costume = self.current_image_filename
        elif not hasattr(self, "_pre_walk_costume"):
            self._pre_walk_costume = "pulchra_overlay_standing.png"

        # CRITICAL HOOK: Make absolutely sure the new costumes are permanently cached as the pre-walk costume baseline
        if self.current_image_filename in ["pulchra_overlay_casual.png", "pulchra_overlay_burnt.png"]:
            self._pre_walk_costume = self.current_image_filename

        # Calculate screen and window metrics
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        win_w = self.root.winfo_width()
        win_h = self.root.winfo_height()
        
        node_coordinates = {
            "top_left": (0, 0),
            "top_center": ((screen_w - win_w) // 2, 0),
            "top_right": (screen_w - win_w, 0),
            "middle_left": (0, (screen_h - win_h) // 2),
            "middle_right": (screen_w - win_w, (screen_h - win_h) // 2),
            "bottom_left": (0, screen_h - win_h - 40),
            "bottom_center": ((screen_w - win_w) // 2, screen_h - win_h - 40),
            "bottom_right": (screen_w - win_w - 100, screen_h - win_h - 70)
        }
        
        tx, ty = node_coordinates.get(target_node, (screen_w - win_w - 30, screen_h - win_h - 70))
        cx, cy = self.root.winfo_x(), self.root.winfo_y()
        path_waypoints = []
        
        # Verify edge positions
        is_on_left = abs(cx - 0) < 60
        is_on_right = abs(cx - (screen_w - win_w)) < 100
        is_on_top = abs(cy - 0) < 60
        is_on_bottom = abs(cy - (screen_h - win_h)) < 120
        
        # Rescue if in middle
        if not (is_on_left or is_on_right or is_on_top or is_on_bottom):
            distances = {"left": cx, "right": (screen_w - win_w) - cx, "top": cy, "bottom": (screen_h - win_h - 70) - cy}
            closest_edge = min(distances, key=distances.get)
            if closest_edge == "left": cx = 0
            elif closest_edge == "right": cx = screen_w - win_w - 30
            elif closest_edge == "top": cy = 0
            else: cy = screen_h - win_h - 70
            path_waypoints.append((cx, cy))

        # Build non-diagonal path corners
        if cx != tx and cy != ty:
            if tx == 0 or tx == (screen_w - win_w):
                path_waypoints.append((tx, cy))
            else:
                path_waypoints.append((cx, ty))
                
        path_waypoints.append((tx, ty))
        self._execute_path_queue(path_waypoints)

    def cancel_active_walk(self):
        # 1. Kill the active movement clock step
        if hasattr(self, '_active_glide_id') and self._active_glide_id:
            self.root.after_cancel(self._active_glide_id)
            self._active_glide_id = None
            
        # 2. Wipe the frame pool memory cache
        if hasattr(self, "_walk_pool"): 
            delattr(self, "_walk_pool")
            
        # 3. Restore her original costume safely
        fallback = getattr(self, "_pre_walk_costume", "pulchra_overlay_standing.png")
        self.change_costume(fallback)
        
        # 4. Trigger an interactive chat bubble confirming she stopped
        cancel_quotes = [
            "I'm stopping here. Did a more profitable commission drop, or are you just indecisive?",
            "I'll just anchor down right here for a bit.",
            "Ugh, picking a route and sticking to it isn't your strong suit, is it? Fine, I'm staying put.",
            "Let me know when you actually figure out where we're going.",
            "Fine, I'm cutting the perimeter walk short. Don't make me stand around completely idle for too long."
        ]
        self.trigger_chat_bubble(forced_text=random.choice(cancel_quotes))


    def _execute_path_queue(self, queue):
        if hasattr(self, "_active_walk_direction"):
            delattr(self, "_active_walk_direction")

        if not queue or self.is_pinned or getattr(self, "is_dvd_mode", False):
            self.save_config_profile()
            fallback = getattr(self, "_pre_walk_costume", "pulchra_overlay_standing.png")
            self.change_costume(fallback)
            return
            
        next_target = queue.pop(0)
        tx, ty = next_target
        cx, cy = self.root.winfo_x(), self.root.winfo_y()
        distance = ((tx - cx) ** 2 + (ty - cy) ** 2) ** 0.5

        #higher number = higher speed
        dynamic_steps = max(50, int(distance / 7))
        self._step_glide(tx, ty, steps_remaining=dynamic_steps, total_steps=dynamic_steps, remaining_queue=queue)



    def _step_glide(self, tx, ty, steps_remaining, total_steps=None, remaining_queue=None):
        if total_steps is None:
            total_steps = steps_remaining

        if steps_remaining <= 0 or self.is_pinned:
            if remaining_queue and len(remaining_queue) > 0:
                self._execute_path_queue(remaining_queue)
            else:
                self.save_config_profile()
                fallback = getattr(self, "_pre_walk_costume", "pulchra_overlay_standing.png")
                self.current_image_filename = fallback
                self.load_and_scale_image(initial_run=False)
                if hasattr(self, 'tray_icon'):
                    self.root.after(0, self.tray_icon.update_menu)
            return
            
        cx = self.root.winfo_x()
        cy = self.root.winfo_y()
        
        if not hasattr(self, "_active_walk_direction"):
            dx = tx - cx
            dy = ty - cy
            if abs(dx) >= abs(dy):
                self._active_walk_direction = "right" if dx >= 0 else "left"
            else:
                self._active_walk_direction = "down" if dy > 0 else "up"

        elapsed_steps = total_steps - steps_remaining
        frames_list = self._walking_photo_cache.get(self._active_walk_direction, [])
        
        if frames_list:
            frame_index = (elapsed_steps // 6) % len(frames_list)
            frame_img = frames_list[frame_index]
            if self.is_flipped:
                frame_img = frame_img.transpose(Image.FLIP_LEFT_RIGHT)
                
            base_height = self.target_height
            target_h = int(base_height * self.current_scale)
            aspect_ratio = frame_img.width / frame_img.height
            target_w = int(target_h * aspect_ratio)
            resized_frame = frame_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
            
            # CRITICAL FIX: Strip fuzzy magenta edges caused by upscaling interpolation
            datas = resized_frame.get_flattened_data()
            clean_data = []
            for px in datas:
                if px[3] < 180: # Hard clip semi-transparent pixel anti-aliasing artifacts
                    clean_data.append((255, 0, 255, 0))
                else:
                    clean_data.append(px)
            resized_frame.putdata(clean_data)
            
            bg_sheet = Image.new("RGBA", resized_frame.size, (255, 0, 255, platform_support.image_background_alpha))
            bg_sheet.alpha_composite(resized_frame)
            
            self.photo = ImageTk.PhotoImage(bg_sheet)
            self.label.config(image=self.photo)
            self.shape_linux_window(resized_frame)

        nx = cx + (tx - cx) // steps_remaining
        ny = cy + (ty - cy) // steps_remaining
        
        bob_offset = 0
        if self._active_walk_direction in ["right", "left"]:
            bob_offset = int(math.sin(elapsed_steps * 0.22) * 1.5)
        #lower values equals flatter wave

        img_w = self.photo.width() if hasattr(self, 'photo') else 100
        img_h = self.photo.height() if hasattr(self, 'photo') else 300
        self.root.geometry(f"{img_w}x{img_h}+{nx}+{ny + bob_offset}")

        if self.bubble_window and self.bubble_window.winfo_exists():
            self.update_bubble_position()
            
        self._active_glide_id = self.root.after(20, lambda: self._step_glide(tx, ty, steps_remaining - 1, total_steps, remaining_queue))

    def quit_application(self):
        self.save_config_profile()
        if self.chat_timer_id: self.root.after_cancel(self.chat_timer_id)
        if self.timer_loop_id: self.root.after_cancel(self.timer_loop_id)
        if self.monitor_loop_id: self.root.after_cancel(self.monitor_loop_id)
        if hasattr(self, "_clip_loop_id"): self.root.after_cancel(self._clip_loop_id)
        
        # Clear background walking loops before window closure
        if getattr(self, "_walk_loop_id", None): self.root.after_cancel(self._walk_loop_id)
        if getattr(self, "_active_glide_id", None): self.root.after_cancel(self._active_glide_id)
        
        # Clear sentinel and costume loops before window closure
        if getattr(self, "_time_sentinel_id", None): self.root.after_cancel(self._time_sentinel_id)
        if getattr(self, "_costume_swapper_id", None): self.root.after_cancel(self._costume_swapper_id)

        if getattr(self, "afk_loop_id", None): 
            self.root.after_cancel(self.afk_loop_id)

        self.close_chat_bubble()
        try: self.tray_icon.stop()
        except Exception: pass
        self.root.destroy()

    def trigger_boot_greeting(self):
        if self.is_click_through: 
            return
        
        current_time_struct = time.localtime()
        current_hour = current_time_struct.tm_hour
        
        # Format current day string as "YYYY-MM-DD"
        today_str = f"{current_time_struct.tm_year}-{current_time_struct.tm_mon:02d}-{current_time_struct.tm_mday:02d}"
        
        # Check if this is the absolute first session sequence today
        has_logged_today = getattr(self, "last_login_date", None) == today_str
        
        if not has_logged_today:
            self.last_login_date = today_str
            # Inject daily check rewards directly into your trust calculation blocks
            if hasattr(self, 'var_freeze_trust') and not self.var_freeze_trust.get():
                if hasattr(self, 'trust_points'):
                    self.trust_points = min(200, self.trust_points + 10)  # +10 points capped at 200 max
            self.save_config_profile()
        
        if 5 <= current_hour < 12:
            greetings = [
                "Morning. You're up early. Let's make this session quick and productive.",
                "Sun's up, day's clearing. Ready to knock out some tasks?",
                "Early bird gets the commission payoff. Let's look over the project.",
                "You're awake? Good. Let's see what you've got queued up today.",
                "Morning grind starts now. Keep your head down and stay sharp."
            ]
        elif 12 <= current_hour < 18:
            greetings = [
                "Afternoon slump? Don't let your pacing drag down our progress.",
                "Midday check-in. What are we scrolling through right now?",
                "Sun's high. Wrap up those open threads so we can get out early.",
                "Back at the desktop? Let's check the workspace logs and finish up.",
                "Just checking the perimeter. Looks like you're still clicking away."
            ]
        else:
            greetings = [
                "Late-night programming? That's when the real work happens.",
                "The server room is quiet. Perfect time to focus without distractions.",
                "Still typing at this hour? Don't fall asleep at your workstation.",
                "Night owl hours. Let's push this compile through and pack it up.",
                "Dark out there. Wrap up this commission thread so we can log off."
            ]
            
        # Append a custom notification flag statement if the reward applied successfully
        final_msg = random.choice(greetings)
        if not has_logged_today:
            final_msg += "\n\n(Daily Login Payout Collected: +10 Trust!)"
            
        self.root.after(800, lambda: self.trigger_chat_bubble(forced_text=final_msg))

    def trigger_pulse_check(self):
        if self.is_click_through: 
            return
        if psutil is None:
            messagebox.showwarning("Missing Library", "Run 'pip install psutil' in terminal to look at metrics.")
            return

        # --- TELEMETRY AUDIT APPRECIATION GAIN ---
        if hasattr(self, 'var_freeze_trust') and not self.var_freeze_trust.get():
            if hasattr(self, 'trust_points'):
                self.trust_points = min(200, self.trust_points + 1)
                self.save_config_profile()

        # 1. Capture system stats instantly
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        batt_info = psutil.sensors_battery()
        
        # 2. Take the initial network baseline snapshot
        net_start = psutil.net_io_counters()
        start_time = time.time()
        
        # 3. This internal function runs exactly 300 milliseconds later
        def process_network_snapshot():
            net_end = psutil.net_io_counters()
            dt = time.time() - start_time
            adjusted_dt = dt if dt > 0 else 0.001
            
            # Calculate live speed (Bytes transferred divided by elapsed seconds)
            bytes_recv_speed = (net_end.bytes_recv - net_start.bytes_recv) / adjusted_dt
            bytes_sent_speed = (net_end.bytes_sent - net_start.bytes_sent) / adjusted_dt
            
            # Convert Bytes/sec to Megabytes/sec
            mb_down = round(bytes_recv_speed / (1024 * 1024), 2)
            mb_up = round(bytes_sent_speed / (1024 * 1024), 2)
            
            # 4. Build and display the live diagnostic report
            pulse_text = f"--- System Pulse Check ---\n"
            pulse_text += f"• CPU Load: {cpu}%\n"
            pulse_text += f"• RAM Usage: {ram}%\n"
            pulse_text += f"• Net Speed: ↓{mb_down} MB/s | ↑{mb_up} MB/s"
            
            if batt_info:
                status = "Charging" if batt_info.power_plugged else "Unplugged"
                pulse_text += f"\n• Battery: {batt_info.percent}% ({status})"
            else:
                pulse_text += "\n• Battery: Desktop Node"
                
            self.trigger_chat_bubble(forced_text=pulse_text)

        # Delay the calculation by 300ms to allow a small data window to accumulate
        self.root.after(300, process_network_snapshot)

    def snap_to_screen_node(self, target_node):
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        win_w = self.root.winfo_width()
        win_h = self.root.winfo_height()
        
        node_coordinates = {
            "top_left": (0, 0),
            "top_center": ((screen_w - win_w) // 2, 0),
            "top_right": (screen_w - win_w, 0),
            "middle_left": (0, (screen_h - win_h) // 2),
            "middle_right": (screen_w - win_w, (screen_h - win_h) // 2),
            "bottom_left": (0, screen_h - win_h - 40),
            "bottom_center": ((screen_w - win_w) // 2, screen_h - win_h - 40),
            "bottom_right": (screen_w - win_w - 30, screen_h - win_h - 70)
        }
        
        new_x, new_y = node_coordinates.get(target_node, (screen_w - win_w - 30, screen_h - win_h - 70))
        self.root.geometry(f"+{new_x}+{new_y}")
        self.save_config_profile()
        if self.bubble_window and self.bubble_window.winfo_exists():
            self.update_bubble_position()

    def save_current_as_home_anchor(self):
        self.root.update_idletasks()
        self.home_x = self.root.winfo_x()
        self.home_y = self.root.winfo_y()
        self.save_config_profile()
        self.trigger_chat_bubble(forced_text="Custom home anchor locked to these coordinates!")

    def go_to_home_anchor(self):
        if self.home_x is not None and self.home_y is not None:
            self.root.geometry(f"+{self.home_x}+{self.home_y}")
            self.save_config_profile()
            if self.bubble_window and self.bubble_window.winfo_exists():
                self.update_bubble_position()
        else:
            self.trigger_chat_bubble(forced_text="No home anchor configured yet. Use the Config Panel to set one.")


    def snap_to_closest_node(self):
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        win_w = self.root.winfo_width()
        win_h = self.root.winfo_height()
        
        current_x = self.root.winfo_x()
        current_y = self.root.winfo_y()
        
        node_coordinates = {
            "top_left": (0, 0),
            "top_center": ((screen_w - win_w) // 2, 0),
            "top_right": (screen_w - win_w, 0),
            "middle_left": (0, (screen_h - win_h) // 2),
            "middle_right": (screen_w - win_w, (screen_h - win_h) // 2),
            "bottom_left": (0, screen_h - win_h - 40),
            "bottom_center": ((screen_w - win_w) // 2, screen_h - win_h - 40),
            "bottom_right": (screen_w - win_w - 30, screen_h - win_h - 70)
        }
        
        closest_node = None
        min_distance = float('inf')
        
        for node_name, (nx, ny) in node_coordinates.items():
            # Use distance math formulas to find the absolute closest spatial point
            distance = ((current_x - nx) ** 2 + (current_y - ny) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                closest_node = node_name
                
        if closest_node:
            self.snap_to_screen_node(closest_node)

    def handle_file_drop(self, event):
        if self.is_click_through:
            return
            
        file_path = event.data.strip('{}')
        base_name = os.path.basename(file_path).lower()
        _, ext = os.path.splitext(base_name)

        # 1. CHECK EXTENSIONS FIRST
        if ext in ['.py', '.js', '.cpp', '.html', '.css']:
            quotes = [
                f"A {ext} file? Let me guess... more messy code for me to look at.",
                "Dropping your scripts on me won't make your project compile any faster.",
                "Let's see if this code is actually good, or if it's just a bunch of typos.",
                "More lines of code? I really hope you actually commented your variables this time.",
                "Another script. Let's just pray it doesn't break the whole system."
            ]
        elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
            quotes = [
                "An image? Don't even think about replacing me with that.",
                "Just checking out the picture. Looks clean enough, I guess.",
                "Are you actually collecting good assets, or just hoarding random images?",
                "A picture file? Don't go trying to change my look on screen without asking.",
                "Image logged. Not bad, but it's definitely not matching my aesthetic."
            ]
        elif ext in ['.txt', '.md', '.json', '.cfg']:
            quotes = [
                "A text file? Keep your folders organized, I hate messy desktops.",
                "Reading your notes now... spreadsheet logs, or just random reminders?",
                "If this is a settings file, make sure you didn't break the formatting syntax.",
                "Plain text. Planning a secret project, or just typing up random thoughts?",
                "Log files? Let's see what kind of terminal errors you're keeping in here."
            ]
        elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz']:
            quotes = [
                "A zip file? Make sure you actually extract the stuff before trying to run it.",
                "Zipped folders are always a gamble. Hope there's no bomb in there.",
                "Mind telling me what's packed inside this archive before you drop it on me?",
                "A compressed folder? Heavy encryption blocks, or just a bunch of loose files?",
                "Zip folder logged. Let's keep our workstation nice and tidy, alright?"
            ]
            
        # 2. CHECK KEYWORDS SECOND IF NO SPECIAL EXTENSION MATCHED
        elif "catnip" in base_name:
            self.change_costume("pulchra_overlay_thinking.png")
            quotes = [
                "Catnip? Seriously? I'm a Thiren mercenary, not some street stray you can bribe with garden weeds.",
                "Are you trying to distract me or just mess with me? ...Though, that scent is actually pretty sharp."
            ]
        elif "burnice" in base_name:
            self.change_costume("pulchra_overlay_thinking.png")
            quotes = [
                "Wait, Burnice? Tell me she didn't bring her fuel tanks near my desktop partition. Back up the logs!",
                "If this file starts smelling like Nitro-Fuel, I'm force-closing this entire application."
            ]
        elif "pulchra" in base_name:
            self.change_costume("pulchra_overlay_thinking.png")
            quotes = [
                "Wait... why does that file have my name on it? What are you hiding in there?",
                "Hold on, are you keeping a secret dossier on me? Let me see what's in that folder!"
            ]
        else:
            quotes = [
                "What am I supposed to do with this random file?",
                "Dropping unknown files onto my corner of the desktop? Bold move."
            ]
            
        # --- AWARD TRUST FOR ALL SUCCESSFUL SECURE DATA TRANSFERS ---
        if hasattr(self, 'var_freeze_trust') and not self.var_freeze_trust.get():
            if hasattr(self, 'trust_points'):
                self.trust_points = min(200, self.trust_points + 3)
                self.save_config_profile()


        self.root.after(0, lambda: self.trigger_chat_bubble(forced_text=random.choice(quotes)))


    def start_time_sentinel_loop(self):
        current_time = time.localtime()
        mins = current_time.tm_min
        secs = current_time.tm_sec

        # Clean up legacy ticks to guarantee single-instance ownership
        if getattr(self, "_time_sentinel_id", None) is not None:
            try:
                self.root.after_cancel(self._time_sentinel_id)
            except Exception:
                pass
            self._time_sentinel_id = None

        if getattr(self, "is_dvd_mode", False):
            ms_until_next_minute = max(1000, (60 - secs) * 1000)
            self._time_sentinel_id = self.root.after(ms_until_next_minute, self.start_time_sentinel_loop)
            return

        if self.alarm_time_str:
            now_str = f"{current_time.tm_hour:02d}:{mins:02d}"
            if now_str == self.alarm_time_str:
                if not self.alarm_triggered_today:
                    self.alarm_triggered_today = True
                    self.trigger_persistent_alarm_popup()
            else:
                self.alarm_triggered_today = False

        if mins == 0 or mins == 30:
            checkpoint_id = (current_time.tm_hour, mins)
            if getattr(self, "_last_triggered_half_hour", None) != checkpoint_id:
                self._last_triggered_half_hour = checkpoint_id
                self.trigger_half_hour_comment(current_time.tm_hour, mins)
        
        ms_until_next_minute = max(1000, (60 - secs) * 1000)
        self._time_sentinel_id = self.root.after(ms_until_next_minute, self.start_time_sentinel_loop)

    def trigger_half_hour_comment(self, hour, minute):
        time_key = f"{hour:02d}:{minute:02d}"
        
        # Comprehensive 48-slot timetable matrix
        timetable = {
            # --- Late Night / Dead Hours ---
            "00:00": "Midnight strike. The desktop grid is officially entering dark cycling.",
            "00:30": "12:30 AM. Still compiling lines? Your focus window is getting narrow.",
            "01:00": "01:00 AM. Terminal noise is down to zero. Why are we still running tabs?",
            "01:30": "01:30 AM. Don't push your luck with system fatigue. Wrap up the thread.",
            "02:00": "02:00 AM. Total radio silence. Even the server fans are cooling down. Go sleep.",
            "02:30": "02:30 AM. Deep night telemetry active. Your screen glare is blinding my layout.",
            "03:00": "03:00 AM. Only automated scripts and insomniacs are awake right now. Which one are you?",
            "03:30": "03:30 AM. Your processing efficiency is cratering at this hour. Close the editor.",
            "04:00": "04:00 AM. The ultimate dead zone. Even the network transit speeds are lagging.",
            "04:30": "04:30 AM. Almost dawn. This isn't a grind anymore, it's just reckless data management.",
            
            # --- Early Morning Transition ---
            "05:00": "05:00 AM. First light hitting the partition. Are you waking up early or sleeping late?",
            "05:30": "05:30 AM. Pre-dawn check. The environment layout looks quiet.",
            "06:00": "06:00 AM. The morning shift begins. Let's see what task pipelines you have queued up.",
            "06:30": "06:30 AM. 06:30 AM already? You're burning through the early hours fast.",
            "07:00": "07:00 AM. Top of the hour. Clear out the leftover trash logs from yesterday.",
            "07:30": "07:30 AM. Mid-morning approach. Grab some fuel before your internal battery hits zero.",
            
            # --- Standard Morning Work Hours ---
            "08:00": "08:00 AM. Official session initiation. Keep your head down and watch the code parameters.",
            "08:30": "08:30 AM. First half-hour block cleared. Pacing looks optimal, don't stall out.",
            "09:00": "09:00 AM. 09:00 AM milestone. The network traffic is starting to spike out there.",
            "09:30": "09:30 AM. Don't overthink the variables. Keep the formatting streamlined.",
            "10:00": "10:00 AM. Two hours deep into the standard shift grid. Are we making progress or just clicking?",
            "10:30": "10:30 AM. Mid-morning slump alert. Stretch your claws before your typing posture locks up.",
            "11:00": "11:00 AM. The standard lunch countdown has officially initialized.",
            "11:30": "11:30 AM. Almost midday. Complete your active loops so you can step away cleanly.",
            
            # --- Midday / Afternoon Transition ---
            "12:00": "High noon. Drop the tools, clear the IDE layout, and go get some food.",
            "12:30": "Half past noon. Don't drip lunch grease on my corner of the monitor.",
            "13:00": "Back to the terminal. Let's push through the afternoon commission logs.",
            "13:30": "1:30 PM slump incoming. Keep your focus sharp so you don't get blindsided.",
            "14:00": "The mid-afternoon grind is a high-risk zone for typos. Double check your typing.",
            "14:30": "Another half hour vaporized into desktop telemetry. Pacing looks steady.",
            "15:00": "3:00 PM checkpoint. The processing pipeline is getting heavy.",
            "15:30": "Coffee or an energy recharge cycle right about now wouldn't hurt your metrics.",
            "16:00": "Kiwi mark strike. The standard business day is entering its final quadrant.",
            "16:30": "4:30 PM. Sun's starting to dip down depending on your server zone.",
            "17:00": "5:00 PM milestone. Most nodes are logging off. What's our status?",
            "17:30": "It's 5:30 PM. Standard pipeline is winding down. Wrap up your active threads.",
            
            # --- Evening / Night Cycling ---
            "18:00": "Evening shift sequence active. Don't tell me we're doing overtime commissions?",
            "18:30": "Desk lamps on, screen brightness adjusted. Settling in for a night session?",
            "19:00": "7:00 PM. Prime relaxation hours, yet you're still auditing this layout.",
            "19:30": "Half past seven. Your system pulses are running smooth.",
            "20:00": "8:00 PM prime milestone. Are we running high-priority tasks or just killing time?",
            "20:30": "Don't lose your pacing. Consistency is what gets the payout.",
            "21:00": "9:00 PM. The desktop environment is getting chill. Don't stress over minor blocks.",
            "21:30": "Late evening checkpoint. Don't let your optimization fall apart now.",
            "22:00": "10:00 PM boundary strike. Time to start winding down your terminal logic.",
            "22:30": "Half-hour warnings till late-night block. Finish up that final compile script.",
            "23:00": "11:00 PM milestone. The grid is going quiet out there.",
            "23:30": "It's 11:30 PM. Keeping the workstation lit up past midnight is high risk. Log off soon."
        }
        
        line = timetable.get(time_key, f"Interval milestone logged: [{time_key}]. Auditing the environment parameters.")
        self.trigger_chat_bubble(forced_text=line)

    def prompt_custom_alarm(self):
        t = simpledialog.askstring("Set Alarm Clock", "Enter time (24-hour HH:MM):\nExample: 14:30", parent=self.root)
        if t:
            t = t.strip()
            # --- FIXED VALIDATION RULE ---
            if len(t) == 5 and t[2] == ":":
                self.alarm_time_str = t
                self.alarm_triggered_today = False
                self.save_config_profile()
                self.trigger_chat_bubble(forced_text=f"Alarm locked in for {t}.")
            else:
                messagebox.showerror("Format Error", "Use 24-hour HH:MM notation.")


    def clear_active_alarm(self):
        self.alarm_time_str = None
        self.alarm_triggered_today = False
        self.save_config_profile()
        self.trigger_chat_bubble(forced_text="Alarm cleared.")
        
    def trigger_persistent_alarm_popup(self):
        if self.is_click_through:
            return
        self.close_chat_bubble()
        
        self.bubble_window = tk.Toplevel(self.root)
        self.bubble_window.overrideredirect(True)
        self.bubble_window.wm_attributes("-topmost", True)
        self.bubble_window.attributes("-alpha", self.current_opacity)
        try: self.bubble_window.wm_attributes("-transparentcolor", "#FF00FF")
        except Exception: pass
        configure_transparency(self.bubble_window)

        msg = f" ALARM [{self.alarm_time_str}] \nClick to dismiss."
        px, py, mw = 12, 8, 160
        
        lbl = tk.Label(self.bubble_window, text=msg, font=("Segoe UI", 9, "bold"), wraplength=mw)
        lbl.update_idletasks()
        tw, th = lbl.winfo_reqwidth(), lbl.winfo_reqheight()
        lbl.destroy()
        
        bw, bh, th_h = tw + (px * 2), th + (py * 2), 8
        canvas = tk.Canvas(self.bubble_window, width=bw, height=bh + th_h, bg="#FF00FF", bd=0, highlightthickness=0)
        canvas.pack()
        
        banner_bg = "#24292e"
        r = 8
        canvas.create_oval(0, 0, r*2, r*2, fill=banner_bg, outline=banner_bg)
        canvas.create_oval(bw - r*2, 0, bw, r*2, fill=banner_bg, outline=banner_bg)
        canvas.create_oval(0, bh - r*2, r*2, bh, fill=banner_bg, outline=banner_bg)
        canvas.create_oval(bw - r*2, bh - r*2, bw, bh, fill=banner_bg, outline=banner_bg)
        canvas.create_rectangle(r, 0, bw - r, bh, fill=banner_bg, outline=banner_bg)
        canvas.create_rectangle(0, r, bw, bh - r, fill=banner_bg, outline=banner_bg)
        
        tw_half, tx = 6, bw // 2
        canvas.create_polygon(tx - tw_half, bh - 1, tx + tw_half, bh - 1, tx, bh + th_h, fill=banner_bg, outline=banner_bg)
        canvas.create_text(bw // 2, bh // 2, text=msg, fill="#e1e4e8", font=("Segoe UI", 9, "bold"), width=mw, justify="center")
        
        self.update_bubble_position()
        
        # --- MODIFIED DISMISS BINDER TO INCLUDE TRUST GAIN ---
        def dismiss_alarm(event):
            if hasattr(self, 'var_freeze_trust') and not self.var_freeze_trust.get():
                if hasattr(self, 'trust_points'):
                    self.trust_points = min(200, self.trust_points + 5)
                    self.save_config_profile()
            self.close_chat_bubble()
            
        canvas.bind("<Button-1>", dismiss_alarm)


    def trigger_persistent_timer_popup(self):
        if self.is_click_through:
            return
        self.close_chat_bubble()
        
        self.bubble_window = tk.Toplevel(self.root)
        self.bubble_window.overrideredirect(True)
        self.bubble_window.wm_attributes("-topmost", True)
        self.bubble_window.attributes("-alpha", self.current_opacity)
        try: self.bubble_window.wm_attributes("-transparentcolor", "#FF00FF")
        except Exception: pass
        configure_transparency(self.bubble_window)
        
        msg = "Contract complete. Time is up, collect your payout.\n\n Click to dismiss"
        px, py, mw = 12, 8, 160
        
        lbl = tk.Label(self.bubble_window, text=msg, font=("Segoe UI", 9, "bold"), wraplength=mw)
        lbl.update_idletasks()
        tw, th = lbl.winfo_reqwidth(), lbl.winfo_reqheight()
        lbl.destroy()
        
        bw, bh, th_h = tw + (px * 2), th + (py * 2), 8
        canvas = tk.Canvas(self.bubble_window, width=bw, height=bh + th_h, bg="#FF00FF", bd=0, highlightthickness=0)
        canvas.pack()
        
        banner_bg = "#24292e"
        r = 8
        canvas.create_oval(0, 0, r*2, r*2, fill=banner_bg, outline=banner_bg)
        canvas.create_oval(bw - r*2, 0, bw, r*2, fill=banner_bg, outline=banner_bg)
        canvas.create_oval(0, bh - r*2, r*2, bh, fill=banner_bg, outline=banner_bg)
        canvas.create_oval(bw - r*2, bh - r*2, bw, bh, fill=banner_bg, outline=banner_bg)
        canvas.create_rectangle(r, 0, bw - r, bh, fill=banner_bg, outline=banner_bg)
        canvas.create_rectangle(0, r, bw, bh - r, fill=banner_bg, outline=banner_bg)
        
        tw_half, tx = 6, bw // 2
        canvas.create_polygon(tx - tw_half, bh - 1, tx + tw_half, bh - 1, tx, bh + th_h, fill=banner_bg, outline=banner_bg)
        canvas.create_text(bw // 2, bh // 2, text=msg, fill="#e1e4e8", font=("Segoe UI", 9, "bold"), width=mw, justify="center")
        
        self.update_bubble_position()
        canvas.bind("<Button-1>", lambda e: self.close_chat_bubble())

    def start_costume_swapper_loop(self):
        if not self.var_swapper.get():
            self._costume_swapper_id = None
            return

        costumes = [
            "pulchra_overlay_standing.png",
            "pulchra_overlay_sitting.png",
            "pulchra_overlay_casual.png",
            "pulchra_overlay_burnt.png",
            "pulchra_overlay_action_1.png",
            "pulchra_overlay_action_2.png",
            "pulchra_nomask_action.png", 
            "pulchra_nomask_sitting.png", 
            "pulchra_overlay_tail.png",
            "pulchra_overlay_thinking.png"
        ]
        
        new_costume = random.choice(costumes)
        self.change_costume(new_costume)
        cooldown_ms = self.var_swap_cooldown.get() * 1000
        self._costume_swapper_id = self.root.after(cooldown_ms, self.start_costume_swapper_loop)

    def toggle_costume_swapper(self):
        self._swapper_state = self.var_swapper.get()
        
        if hasattr(self, "_costume_swapper_id") and self._costume_swapper_id is not None:
            try:
                self.root.after_cancel(self._costume_swapper_id)
            except Exception:
                pass
            self._costume_swapper_id = None
            
        if hasattr(self, 'tray_icon'): 
            self.root.after(0, self.tray_icon.update_menu)
            
        if self.var_swapper.get() and not getattr(self, "is_afk", False) and not getattr(self, "is_dvd_mode", False):
            self.start_costume_swapper_loop()
        self.save_config_profile()


    def toggle_click_irritation_system(self):
        self.click_irritation_enabled = self.var_irritation.get()
        self.click_streak_count = 0  # Reset counter when toggled
        self.save_config_profile()
        if hasattr(self, 'tray_icon'):
            self.root.after(0, self.tray_icon.update_menu)

    def toggle_edge_snapping(self):
        # Let idletasks catch up so the Tkinter BooleanVar registers the new state
        self.root.update_idletasks()
        self.save_config_profile()
            
    def safe_tray_toggle_irritation(self):
        self.root.after(0, lambda: [
            self.var_irritation.set(not self.var_irritation.get()),
            self.toggle_click_irritation_system()
        ])

    def prompt_custom_name(self):
        pop = tk.Toplevel(self.root, bg="#1e1e1e")
        pop.title("Proxy Registration")
        pop.resizable(False, False)
        pop.wm_attributes("-topmost", True)
        
        sw, sh = pop.winfo_screenwidth(), pop.winfo_screenheight()
        cx, cy = (sw // 2) - (150), (sh // 2) - (60)
        pop.geometry(f"300x120+{cx}+{cy}")

        # Dark theme interface elements
        tk.Label(pop, text="Enter your name, Proxy:", bg="#1e1e1e", fg="#e1e4e8", font=("Segoe UI", 9, "bold")).pack(pady=(12, 6))
        
        entry = tk.Entry(pop, bg="#2d2d2d", fg="white", insertbackground="white", bd=0, highlightthickness=1, highlightbackground="#444", font=("Segoe UI", 10))
        entry.pack(fill="x", padx=20, pady=4)
        entry.insert(0, self.user_name)
        entry.focus_force()

        def save_and_close(event=None):
            name = entry.get().strip()
            if name:
                self.user_name = name
                self.save_config_profile()
                self.trigger_chat_bubble(forced_text=f"System profile logged. I'll call you {self.user_name} from now on.")
            pop.destroy()

        # Custom themed submission button layout
        tk.Button(pop, text="Confirm Link", command=save_and_close, bg="#2d2d2d", fg="white", bd=0, pady=6, font=("Segoe UI", 9)).pack(fill="x", padx=20, pady=(10, 0))        

        pop.bind("<Return>", save_and_close)
        pop.bind("<Escape>", lambda e: pop.destroy())

    def _get_system_idle_time(self):
        return platform_support.idle_seconds()

    def start_afk_sentinel_loop(self):
        if getattr(self, "afk_loop_id", None):
            self.root.after_cancel(self.afk_loop_id)
            
        idle_seconds = self._get_system_idle_time()
        
        stage_1_threshold = float(self.var_afk_cooldown.get())
        stage_2_threshold = stage_1_threshold * 2.0  # Stage 2 automatically scales out to double Stage 1


        if idle_seconds >= stage_1_threshold:
            # User is inactive! Evaluate which slacker stage she should be in
            self.enter_afk_state(idle_seconds, stage_2_threshold)
        else:
            # User moved the mouse or typed -> Wake up if she was asleep!
            if getattr(self, "is_afk", False):
                self.exit_afk_state()
            
        self.afk_loop_id = self.root.after(2000, self.start_afk_sentinel_loop)

    def enter_afk_state(self, idle_seconds, stage_2_threshold):
        if self.is_click_through: 
            return
            
        # --- FIXED INITIALIZATION PASS ---
        if not self.is_afk:
            if "walking" not in self.current_image_filename and self.current_image_filename not in [
                "pulchra_overlay_sitting.png", "pulchra_nomask_sitting.png", 
                "pulchra_overlay_casual.png", "pulchra_overlay_burnt.png"
            ]:
                self._pre_afk_costume = self.current_image_filename
            else:
                self._pre_afk_costume = self.current_image_filename 

            self.is_afk = True
            
            # Safely suspend the automatic costume swapper loop
            self._was_swapper_enabled_pre_afk = self.var_swapper.get()
            if self._was_swapper_enabled_pre_afk:
                if getattr(self, "_costume_swapper_id", None):
                    self.root.after_cancel(self._costume_swapper_id)
                    self._costume_swapper_id = None

        # --- CRITICAL FIX: DO NOT OVERWRITE CUSTOM MAIN COSTUMES OVER IDLE CHECKS ---
        if self.current_image_filename in ["pulchra_overlay_casual.png", "pulchra_overlay_burnt.png"]:
            return  # Completely exit the function so your costume stays locked on screen

        # --- LEVEL EVALUATION ENGINE ---
        if idle_seconds >= stage_2_threshold:
            # LEVEL 2: Mask-less Sitting Pose (Deep Slacking)
            if self.current_image_filename != "pulchra_nomask_sitting.png":
                self.current_image_filename = "pulchra_nomask_sitting.png"
                self.root.after(0, self.load_and_scale_image)
                
                level_2_quotes = [
                    "Finally, I can take the mask off... If you're going to be gone this long, I'm off the clock.",
                    "Total silence. Good. My mask was starting to get stuffy anyway.",
                    "Alright, you're clearly out. Don't look at me, I'm taking a break.",
                    "No pointer moving, no typing... Guess I can finally relax for a bit.",
                    "If anyone asks, I'm checking lower memory sectors. But really? I'm napping."
                ]
                self.trigger_chat_bubble(forced_text=random.choice(level_2_quotes))
        else:
            # LEVEL 1: Masked Sitting Pose (Standard Idling)
            if self.current_image_filename != "pulchra_overlay_sitting.png":
                self.current_image_filename = "pulchra_overlay_sitting.png"
                self.root.after(0, self.load_and_scale_image)
                
                level_1_quotes = [
                    "Finally, a breather. I was getting tired of watching you scroll through the same tabs.",
                    "I'm taking a quick break. Don't leave me waiting around all day, Proxy. Time is gear coins.",
                    "Looks like you stepped away. Fine by me, less layout tracking I have to run.",
                    "Staring at a frozen screen is exhausting. I'm taking a break until you get back.",
                    "Gone to grab coffee, or did your brain just freeze up? Whatever, I'm sitting down."
                ]
                self.trigger_chat_bubble(forced_text=random.choice(level_1_quotes))

    def exit_afk_state(self):
        self.is_afk = False
        
        # --- LOCKED RESCUE PASS ---
        restored_costume = getattr(self, "_pre_afk_costume", "pulchra_overlay_standing.png")
        self.change_costume(restored_costume)
        
        # Restore the automatic background costume swapper loop if it was active before you left
        if getattr(self, "_was_swapper_enabled_pre_afk", False):
            self._costume_swapper_id = self.root.after(300000, self.start_costume_swapper_loop)
            
        # 5 Natural defensive wake-up quotes
        wakeup_quotes = [
            "Uh—Proxy! I wasn't slacking off, I promise! I was just... resting a bit.",
            "Whoa! Move that cursor a little louder next time, will ya? You almost startled me.",
            "Back already? Let's just pretend you didn't just catch me napping.",
            "Claws out, mask on... right, let's get back to business. What commission are we running?",
            "Nudge the screen all you want, I'm awake. So, what's our next objective?"
        ]
        self.trigger_chat_bubble(forced_text=random.choice(wakeup_quotes))

        # --- DELAYED SHAKE ENGINE ---
        self.root.after(40, lambda: self.run_window_shake_loop(intensity=8, steps=6))

    def safe_tray_toggle_dvd(self):
        self.root.after(0, self.toggle_dvd_mode)

    def toggle_dvd_mode(self):
        self.is_dvd_mode = not self.is_dvd_mode
        
        # 1. Update the Right-Click menu label style dynamically using your configuration format
        if self.is_dvd_mode:
            self.menu.entryconfigure("DVD Bouncing Mode", label="✓ DVD Bouncing Mode")
        else:
            self.menu.entryconfigure("✓ DVD Bouncing Mode", label="DVD Bouncing Mode")

        # 2. Keep the system tray icon menu items synced up
        if hasattr(self, 'tray_icon'):
            self.root.after(0, self.tray_icon.update_menu)

        if self.is_dvd_mode:
            # Shut down background loops immediately so they don't break positioning
            self.close_chat_bubble()
            
            if self.chat_timer_id:
                self.root.after_cancel(self.chat_timer_id)
                self.chat_timer_id = None
                
            if self._walk_loop_id:
                self.root.after_cancel(self._walk_loop_id)
                self._walk_loop_id = None
                
            if getattr(self, "_active_glide_id", None):
                self.root.after_cancel(self._active_glide_id)
                self._active_glide_id = None
                
            if getattr(self, "afk_loop_id", None):
                self.root.after_cancel(self.afk_loop_id)
                self.afk_loop_id = None
                
            if getattr(self, "_clip_loop_id", None):
                self.root.after_cancel(self._clip_loop_id)
                self._clip_loop_id = None

            # Wake her out of AFK status but leave her current costume intact
            self.is_afk = False
            
            # Start the bounce tick
            self.run_dvd_physics_loop()
        else:
            if getattr(self, "_dvd_loop_id", None):
                self.root.after_cancel(self._dvd_loop_id)
                self._dvd_loop_id = None
            
            self.is_afk = False 
            
            if getattr(self, "afk_loop_id", None):
                self.root.after_cancel(self.afk_loop_id)
            self.afk_loop_id = self.root.after(5000, self.start_afk_sentinel_loop)
            
            if getattr(self, "_costume_swapper_id", None):
                self.root.after_cancel(self._costume_swapper_id)
                self._costume_swapper_id = None
            if self.var_swapper.get():
                self.start_costume_swapper_loop()
                
            self.start_clipboard_monitor_loop()
            
            if self.chat_enabled:
                if getattr(self, "chat_timer_id", None):
                    self.root.after_cancel(self.chat_timer_id)
                self.chat_timer_id = self.root.after(self.var_chat_cooldown.get() * 1000, self.trigger_chat_bubble)

            
            if self.var_patrol.get():
                self.start_random_walk_loop()

    def run_dvd_physics_loop(self):
        if not self.is_dvd_mode:
            return

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        win_w = self.root.winfo_width()
        win_h = self.root.winfo_height()

        # Constraints aligned safely with your manual snap_to_screen_node heights
        max_x = screen_w - win_w
        max_y = screen_h - win_h - 40 

        cx = self.root.winfo_x()
        cy = self.root.winfo_y()

        nx = cx + self.dvd_dx
        ny = cy + self.dvd_dy

        if nx <= 0 or nx >= max_x:
            self.dvd_dx = -self.dvd_dx
            nx = max(0, min(nx, max_x))

        if ny <= 0 or ny >= max_y:
            self.dvd_dy = -self.dvd_dy
            ny = max(0, min(ny, max_y))

        self.root.geometry(f"+{nx}+{ny}")
        self._dvd_loop_id = self.root.after(20, self.run_dvd_physics_loop)


    def open_shortcut_binding_selector_pop(self):
        # Prevent open duplication loops
        if hasattr(self, '_shortcut_pop') and self._shortcut_pop.winfo_exists():
            self._shortcut_pop.lift()
            return

        self._shortcut_pop = tk.Toplevel(self._dash_win, bg="#1e1e1e")
        self._shortcut_pop.title("Shortcut Node Binding")
        self._shortcut_pop.resizable(False, False)
        self._shortcut_pop.wm_attributes("-topmost", True)
        
        sw, sh = self._shortcut_pop.winfo_screenwidth(), self._shortcut_pop.winfo_screenheight()
        cx, cy = (sw // 2) - 160, (sh // 2) - 80
        self._shortcut_pop.geometry(f"320x140+{cx}+{cy}")

        tk.Label(
            self._shortcut_pop, text="Select Head Tap Target Action:", 
            bg="#1e1e1e", fg="#e1e4e8", font=("Segoe UI", 9, "bold")
        ).pack(pady=(15, 6))

        shortcut_map = {
            "System Pulse Check": "pulse",
            "Toggle Chat Bubbles": "chat",
            "Auto-Costume Swap": "swapper",
            "Edge Patrol Walks": "patrol",
            "Resource Monitor": "monitor",
            "Click Irritation Mode": "irritation",
            "Disable Edge Snapping": "snap"
        }


        # Find current friendly name match to pre-populate dropdown view options safely
        current_friendly = "Toggle Chat Bubbles"
        for friendly, code_key in shortcut_map.items():
            if code_key == self.head_shortcut_setting:
                current_friendly = friendly
                break

        var_dropdown_choice = tk.StringVar(value=current_friendly)

        def commit_dropdown_link_change(selection):
            self.head_shortcut_setting = shortcut_map.get(selection, "chat")
            self.save_config_profile()

        opt_menu = tk.OptionMenu(self._shortcut_pop, var_dropdown_choice, *shortcut_map.keys(), command=commit_dropdown_link_change)
        opt_menu.config(bg="#2d2d2d", fg="white", bd=0, highlightthickness=0, activebackground="#3d3d3d", activeforeground="white", font=("Segoe UI", 9), pady=4)
        opt_menu["menu"].config(bg="#1e1e1e", fg="white", activebackground="#2d2d2d")
        opt_menu.pack(fill="x", padx=30, pady=5)

        tk.Button(
            self._shortcut_pop, text="Close & Apply Link", 
            command=self._shortcut_pop.destroy, 
            bg="#2d2d2d", fg="#ff9900", bd=0, pady=6, font=("Segoe UI", 9, "bold")
        ).pack(fill="x", padx=30, pady=(12, 0))

def main():
    from tkinterdnd2 import TkinterDnD
    
    # FIX: Creating the root window directly via TkinterDnD's custom Tk wrapper
    root = TkinterDnD.Tk()
    
    # Initialize your companion app
    app = PulchraDesktopCompanion(root)
    
    # Bind the drag-and-drop mechanics to the root window hooks
    root.drop_target_register('DND_Files')
    root.dnd_bind('<<Drop>>', app.handle_file_drop)
    
    if "--smoke-test" in sys.argv:
        errors = []
        def report_error(*args):
            errors.append(args)
        root.report_callback_exception = report_error
        def smoke():
            try:
                app.apply_click_through()
                app._get_system_idle_time()
                app.trigger_chat_bubble(forced_text="Smoke test")
                app.close_chat_bubble()
                app.open_settings_dashboard() if hasattr(app, "open_settings_dashboard") else None
                app.change_costume("pulchra_overlay_sitting.png")
                app.change_costume("pulchra_overlay_standing.png")
                app.save_config_profile()
            except Exception as error:
                errors.append(error)
            app.quit_application()
        root.after(1200, smoke)
        root.mainloop()
        if errors:
            raise RuntimeError(str(errors))
        print("Smoke test passed")
    else:
        root.mainloop()