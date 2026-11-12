"""Regression coverage for upstream 5.3.1 custom automation intervals."""
import json
from pathlib import Path
import tempfile
import tkinter as tk
import unittest

import test_shortcut_config as config_tests


DEFAULTS = {"cooldown_time": 30, "walk_cooldown": 300,
            "swap_cooldown": 300, "afk_cooldown": 300,
            "chat_cooldown": 30, "monitor_cooldown": 180}


class CooldownConfigTests(unittest.TestCase):
    def make(self, directory):
        app = config_tests.ShortcutConfigTests().make_companion(directory)
        app.head_shortcut_setting = "chat"
        # Real Tk variables exercise .set/.get without creating a desktop.
        app._test_tcl = tk.Tcl()
        for name, value in DEFAULTS.items():
            setattr(app, "var_" + name, tk.IntVar(app._test_tcl, value=value))
        return app

    def test_all_custom_intervals_survive_two_save_reload_cycles(self):
        with tempfile.TemporaryDirectory() as directory:
            app = self.make(directory)
            for values in ((45, 110, 220, 330, 65, 410),
                           (5, 600, 30, 10, 120, 600)):
                expected = dict(zip(DEFAULTS, values))
                for key, value in expected.items():
                    getattr(app, "var_" + key).set(value)
                app.save_config_profile()
                saved = json.loads((Path(directory) / "config.json").read_text())
                self.assertEqual({key: saved.get(key) for key in DEFAULTS}, expected)
                app = self.make(directory)
                app.load_config_profile()
                self.assertEqual({key: getattr(app, "var_" + key).get()
                                  for key in DEFAULTS}, expected)

    def test_old_profile_keeps_existing_interval_and_defaults_missing_ones(self):
        with tempfile.TemporaryDirectory() as directory:
            for profile in ({}, {"cooldown_time": 55, "chat_cooldown": 95}):
                (Path(directory) / "config.json").write_text(json.dumps(profile))
                app = self.make(directory)
                for key in DEFAULTS:
                    getattr(app, "var_" + key).set(999)
                app.load_config_profile()
                self.assertEqual({key: getattr(app, "var_" + key).get()
                                  for key in DEFAULTS}, DEFAULTS | profile)
