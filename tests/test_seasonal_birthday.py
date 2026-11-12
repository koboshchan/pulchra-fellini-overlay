"""Coverage for upstream 5.2.1 seasonal greetings and birthday setting."""
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

    def test_expanded_holiday_pools_and_name_formatting(self):
        # All dates added in upstream 5.2.1, including regional holidays.
        dates = ((2, 14), (3, 8), (3, 17), (5, 4), (5, 18), (7, 1),
                 (7, 4), (7, 14), (9, 7), (9, 13), (9, 25), (9, 30),
                 (10, 12), (11, 11), (11, 27))
        with tempfile.TemporaryDirectory() as d:
            app = self.make(d)
            app.birthday = "07-07"
            app.user_name = "SeasonalTester"
            for month, day in dates:
                for index in (0, -1):
                    with self.subTest(date=(month, day), quote=index):
                        pool = []
                        def choose(options):
                            pool.extend(options)
                            return options[index]
                        with patch("core.companion.random.choice", side_effect=choose):
                            msg = self.greet(app, month, day)
                        self.assertEqual(len(pool), 2)
                        self.assertNotIn("{name}", msg)
                        if "{name}" in pool[index]:
                            self.assertIn("SeasonalTester", msg)
                        self.assertNotIn("Morning.", msg)

    def test_daily_bonus_only_once_and_persists(self):
        with tempfile.TemporaryDirectory() as d:
            app = self.make(d)
            first = self.greet(app, 7, 1)
            self.assertEqual(app.trust_points, 60)
            self.assertIn("Daily Login Bonus Collected: +10 Trust!", first)
            saved = json.loads((Path(d) / "config.json").read_text())
            self.assertEqual(saved["last_login_date"], "2026-07-01")
            reader = self.make(d)
            reader.load_config_profile()
            self.assertEqual(reader.trust_points, 60)
            self.assertNotIn("Daily Login Bonus", self.greet(app, 7, 1))
            self.assertEqual(app.trust_points, 60)
            self.greet(app, 7, 2)
            self.assertEqual(app.trust_points, 70)

    def test_daily_bonus_respects_freeze_and_cap(self):
        with tempfile.TemporaryDirectory() as d:
            app = self.make(d)
            app.trust_points = 195
            self.greet(app, 7, 1)
            self.assertEqual(app.trust_points, 200)
            app.var_freeze_trust.get.return_value = True
            app.trust_points = 50
            self.greet(app, 7, 2)
            self.assertEqual(app.trust_points, 50)

    def test_birthday_overrides_new_holiday(self):
        with tempfile.TemporaryDirectory() as d:
            app = self.make(d)
            app.birthday = "07-01"
            self.assertIn("birthday", self.greet(app, 7, 1).lower())
