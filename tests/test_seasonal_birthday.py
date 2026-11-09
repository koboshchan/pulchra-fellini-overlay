"""Coverage for upstream 5.2.0 seasonal greetings and birthday setting."""
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

from core.companion import PulchraDesktopCompanion
import test_shortcut_config as base


def struct(month, day):
    return time.struct_time((2026, month, day, 10, 0, 0, 0, 1, 0))


class SeasonalBirthdayTests(unittest.TestCase):
    def make(self, directory):
        app = base.ShortcutConfigTests().make_companion(directory)
        app.head_shortcut_setting = "chat"
        app.is_click_through = False
        app.last_login_date = "2026-01-01"
        self.messages = []
        app.root.after = lambda ms, fn: fn()
        app.trigger_chat_bubble = lambda forced_text=None: self.messages.append(forced_text)
        return app

    def greet(self, app, month, day):
        with patch("core.companion.time.localtime", return_value=struct(month, day)):
            app.trigger_boot_greeting()
        return self.messages[-1]

    def test_birthday_persists_and_defaults(self):
        with tempfile.TemporaryDirectory() as d:
            app = self.make(d)
            app.birthday = "03-03"
            app.save_config_profile()
            self.assertEqual(json.loads((Path(d) / "config.json").read_text())["birthday"], "03-03")
            reader = self.make(d)
            reader.load_config_profile()
            self.assertEqual(reader.birthday, "03-03")
            (Path(d) / "config.json").write_text("{}")
            old = self.make(d)
            old.load_config_profile()
            self.assertEqual(old.birthday, "12-15")

    def test_holiday_greeting_uses_name(self):
        with tempfile.TemporaryDirectory() as d:
            app = self.make(d)
            app.birthday = "07-07"
            msg = self.greet(app, 12, 25)
            self.assertIn("Proxy", msg)
            self.assertNotIn("{name}", msg)
            self.assertTrue("Christmas" in msg or "holiday" in msg)

    def test_birthday_overrides_holiday(self):
        with tempfile.TemporaryDirectory() as d:
            app = self.make(d)
            app.birthday = "12-25"
            self.assertIn("birthday", self.greet(app, 12, 25).lower())

    def test_ordinary_day_uses_time_of_day_greeting(self):
        with tempfile.TemporaryDirectory() as d:
            app = self.make(d)
            app.birthday = "07-07"
            msg = self.greet(app, 6, 10)
            self.assertNotIn("birthday", msg.lower())
            self.assertNotIn("{name}", msg)
