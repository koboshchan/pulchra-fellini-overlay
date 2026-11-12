"""Regression coverage for upstream 5.2.2 clipboard costume restoration."""
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from core.companion import PulchraDesktopCompanion

THINKING = "pulchra_overlay_thinking.png"
CASUAL = "pulchra_overlay_casual.png"


class ClipboardCostumeTests(unittest.TestCase):
    def make(self):
        app = PulchraDesktopCompanion.__new__(PulchraDesktopCompanion)
        app.root = Mock()
        self.callbacks = []
        app.root.after.side_effect = lambda ms, fn: self.callbacks.append((ms, fn))
        app.root.clipboard_get.return_value = "new clipboard text"
        app._last_tracked_clipboard = "old clipboard text"
        app.is_click_through = False
        app.current_image_filename = CASUAL
        app._pre_irritation_costume = "pulchra_overlay_standing.png"
        app.click_irritation_enabled = False
        app.last_click_timestamp = 0
        app.current_opacity = 1.0
        app.user_name = "Proxy"
        app.bg_color = "#FF00FF"
        app.var_bubble_light_mode = Mock(get=Mock(return_value=False))
        app.chat_enabled = False
        app.close_chat_bubble = Mock()
        app.update_bubble_position = Mock()
        def change(filename):
            app.current_image_filename = filename
        app.change_costume = Mock(side_effect=change)
        return app

    def bubble(self, app):
        with patch("core.companion.tk.Toplevel"), \
             patch("core.companion.tk.Label") as label, \
             patch("core.companion.tk.Canvas"), \
             patch("core.companion.configure_transparency"):
            label.return_value.winfo_reqwidth.return_value = 100
            label.return_value.winfo_reqheight.return_value = 50
            app.trigger_chat_bubble(forced_text="Clipboard reaction")

    def test_clipboard_remembers_original_even_for_repeated_reactions(self):
        app = self.make()
        app.trigger_chat_bubble = Mock()
        with patch("core.companion.random.random", return_value=0):
            app.start_clipboard_monitor_loop()
            self.assertEqual(app._pre_thinking_costume, CASUAL)
            self.assertEqual(app.current_image_filename, THINKING)
            app.root.clipboard_get.return_value = "another copied message"
            app.start_clipboard_monitor_loop()
        self.assertEqual(app._pre_thinking_costume, CASUAL)
        self.assertEqual([ms for ms, _ in self.callbacks], [4000, 4000])

    def test_restores_clipboard_costume_with_irritation_disabled(self):
        app = self.make()
        app.current_image_filename = THINKING
        app._pre_thinking_costume = CASUAL
        self.bubble(app)
        revert = next(fn for ms, fn in self.callbacks if ms == 15000)
        with patch("core.companion.time.time", return_value=20):
            revert()
        app.change_costume.assert_called_once_with(CASUAL)
        self.assertFalse(hasattr(app, "_pre_thinking_costume"))

    def test_irritation_fallback_still_works(self):
        app = self.make()
        app.current_image_filename = THINKING
        self.bubble(app)
        with patch("core.companion.time.time", return_value=20):
            next(fn for ms, fn in self.callbacks if ms == 15000)()
        app.change_costume.assert_called_once_with(app._pre_irritation_costume)

    def test_does_not_override_manual_costume_or_recent_click(self):
        for manual, timestamp in ((CASUAL, 0), (THINKING, 19)):
            with self.subTest(costume=manual, clicked=timestamp):
                app = self.make()
                app.current_image_filename = THINKING
                app._pre_thinking_costume = CASUAL
                self.bubble(app)
                app.current_image_filename = manual
                app.last_click_timestamp = timestamp
                with patch("core.companion.time.time", return_value=20):
                    next(fn for ms, fn in self.callbacks if ms == 15000)()
                app.change_costume.assert_not_called()
