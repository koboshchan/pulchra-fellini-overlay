"""Regression coverage for upstream 5.1.1's saved head-tap shortcut."""
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from core.companion import PulchraDesktopCompanion


class ShortcutConfigTests(unittest.TestCase):
    def make_companion(self, directory):
        # Exercise the real file persistence without starting a desktop or timers.
        app = PulchraDesktopCompanion.__new__(PulchraDesktopCompanion)
        app.get_script_dir = lambda: directory
        app.root = SimpleNamespace(update_idletasks=lambda: None,
                                   winfo_x=lambda: 100, winfo_y=lambda: 200)
        app.current_scale = app.current_opacity = 1.0
        app.current_image_filename = "pulchra_overlay_standing.png"
        app.is_pinned = app.is_click_through = app.is_flipped = False
        app.chat_enabled = app.monitor_enabled = False
        app.home_x = app.home_y = app.alarm_time_str = None
        app.trust_points = 50
        app.user_name = "Proxy"
        app.mood_states = {}
        for name in ("swapper", "patrol", "irritation", "freeze_trust",
                     "bubble_light_mode", "disable_snap", "cooldown_time"):
            setattr(app, "var_" + name, Mock(get=Mock(return_value=False)))
        return app

    def test_head_shortcut_survives_save_and_reload(self):
        with tempfile.TemporaryDirectory() as directory:
            writer = self.make_companion(directory)
            for shortcut in ("pulse", "chat", "swapper", "patrol", "monitor",
                             "irritation", "snap"):
                with self.subTest(shortcut=shortcut):
                    writer.head_shortcut_setting = shortcut
                    writer.save_config_profile()
                    saved = json.loads((Path(directory) / "config.json").read_text())
                    self.assertEqual(saved["head_shortcut_setting"], shortcut)
                    reader = self.make_companion(directory)
                    reader.load_config_profile()
                    self.assertEqual(reader.head_shortcut_setting, shortcut)

    def test_old_profile_defaults_to_chat(self):
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "config.json").write_text("{}")
            app = self.make_companion(directory)
            app.load_config_profile()
            self.assertEqual(app.head_shortcut_setting, "chat")
