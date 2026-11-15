"""Behavioral coverage for the 5.4.0 high-trust headpat animation."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from core.companion import PulchraDesktopCompanion

class HeadpatHeartTests(unittest.TestCase):
    def make(self):
        app = PulchraDesktopCompanion.__new__(PulchraDesktopCompanion)
        app.root = Mock()
        for key, value in (("width", 200), ("height", 300), ("x", 100), ("y", 200)):
            getattr(app.root, "winfo_" + key).return_value = value
        app.root.winfo_exists.return_value = True
        app.is_click_through = app.is_flipped = app.is_gravity_flipped = False
        app.current_opacity = 0.75
        app.current_image_filename = "test"
        app.costume_click_zones = {"test": ((.1, .2, .3, .4), (.5, .6, .7, .8))}
        app.chat_enabled = app.monitor_enabled = app.click_irritation_enabled = False
        for name in ("chat", "swapper", "patrol", "monitor", "irritation", "disable_snap"):
            setattr(app, "var_" + name, Mock(get=Mock(return_value=False)))
        for name in ("trigger_chat_bubble", "trigger_pulse_check", "toggle_chat_bubbles",
                     "toggle_costume_swapper", "toggle_patrol_system",
                     "toggle_resource_monitor", "toggle_click_irritation_system",
                     "save_config_profile"):
            setattr(app, name, Mock())
        return app

    def test_high_trust_chance_and_every_shortcut_action(self):
        actions = {"pulse": "trigger_pulse_check", "chat": "toggle_chat_bubbles",
                   "swapper": "toggle_costume_swapper", "patrol": "toggle_patrol_system",
                   "monitor": "toggle_resource_monitor",
                   "irritation": "toggle_click_irritation_system",
                   "snap": "save_config_profile", "unbound": "trigger_chat_bubble"}
        for setting, action in actions.items():
            for trust, chance, expected in ((149, 0, False), (150, .499, True),
                                             (200, .5, False), (200, .9, False)):
                with self.subTest(setting=setting, trust=trust, chance=chance):
                    app = self.make()
                    app.trust_points = trust
                    app.head_shortcut_setting = setting
                    order = Mock()
                    getattr(app, action).side_effect = order.action
                    app.trigger_heart_reaction = order.heart
                    with patch("core.companion.random.random", return_value=chance):
                        app.execute_head_shortcut_toggle()
                    getattr(app, action).assert_called_once()
                    self.assertEqual(order.heart.call_count, int(expected))
                    if expected:
                        self.assertEqual([c[0] for c in order.mock_calls], ["action", "heart"])

    def test_three_staggered_hearts_and_click_through_guard(self):
        app = self.make()
        app.trigger_heart_reaction()
        self.assertEqual([c.args[0] for c in app.root.after.call_args_list], [0, 260, 520])
        self.assertTrue(all(c.args[1] == app._spawn_floating_heart
                            for c in app.root.after.call_args_list))
        app.root.after.reset_mock()
        app.is_click_through = True
        app.trigger_heart_reaction()
        app.root.after.assert_not_called()

    def spawn(self, app, jitter=0, callback=None):
        with patch("core.companion.tk.Toplevel") as top, \
             patch("core.companion.tk.Label"), \
             patch("core.companion.ImageTk.PhotoImage"), \
             patch("core.companion.configure_transparency", return_value="#202020") as trans, \
             patch("core.companion.platform_support.shape_window") as shape, \
             patch("core.companion.random.randint", return_value=jitter) as spread:
            heart = top.return_value
            heart.winfo_exists.return_value = True
            (callback or app._spawn_floating_heart)()
            spread.assert_called_once_with(-18, 18)
            trans.assert_called_once_with(heart)
            image = shape.call_args.args[1]
            self.assertEqual(image.size, (30, 30))
            self.assertEqual(image.getpixel((0, 0))[3], 0)
            self.assertGreater(image.getpixel((15, 15))[3], 128)
            return heart

    def test_costume_head_position_follows_both_flips_and_fallback(self):
        for fallback in (False, True):
            for horizontal in (False, True):
                for vertical in (False, True):
                    with self.subTest(fallback=fallback, horizontal=horizontal, vertical=vertical):
                        app = self.make()
                        if fallback:
                            app.costume_click_zones = {}
                        app.is_flipped, app.is_gravity_flipped = horizontal, vertical
                        heart = self.spawn(app)
                        nx, ny = (.5, .05) if fallback else (.2, .2)
                        if horizontal: nx = 1 - nx
                        if vertical: ny = 1 - ny
                        x, y = int(100 + nx * 200 - 15), int(200 + ny * 300 - 22)
                        self.assertEqual(heart.geometry.call_args_list[0].args[0],
                                         f"30x30+{x}+{y}")

    def test_animation_rises_fades_and_destroys_without_looping(self):
        app = self.make()
        callbacks = []
        app.root.after.side_effect = lambda delay, fn: callbacks.append((delay, fn))
        heart = self.spawn(app)
        while callbacks:
            delay, fn = callbacks.pop(0)
            self.assertEqual(delay, 40)
            fn()
        heart.destroy.assert_called_once()
        self.assertEqual(heart.geometry.call_count, 35)
        self.assertEqual(heart.geometry.call_args.args[0], "+123+187")
        alphas = [c.args[1] for c in heart.attributes.call_args_list
                  if c.args[0] == "-alpha"]
        self.assertEqual(alphas[0], .75)
        self.assertLess(alphas[-1], .1)

    def test_destroyed_windows_stop_without_new_callbacks(self):
        app = self.make()
        app.root.winfo_exists.return_value = False
        with patch("core.companion.tk.Toplevel") as top:
            app._spawn_floating_heart()
            top.assert_not_called()
        app = self.make()
        heart = self.spawn(app)
        callback = app.root.after.call_args.args[1]
        app.root.after.reset_mock()
        heart.winfo_exists.return_value = False
        callback()
        app.root.after.assert_not_called()

    def test_no_duplicate_method_can_shadow_costume_aware_implementation(self):
        tree = ast.parse((Path(__file__).resolve().parents[1] / "core/companion.py").read_text())
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef))
        self.assertEqual(sum(isinstance(n, ast.FunctionDef) and n.name == "_spawn_floating_heart"
                             for n in cls.body), 1)


    def test_delayed_hearts_use_current_costume_and_window_position(self):
        app = self.make()
        app.trigger_heart_reaction()
        callbacks = [call.args[1] for call in app.root.after.call_args_list]
        # Moving, resizing, changing costume and flipping before a delayed heart
        # fires must not reuse the old center-of-window spawn from upstream 5.4.0.
        for index, jitter in enumerate((-18, 0, 18)):
            with self.subTest(jitter=jitter):
                app.current_image_filename = "new-costume"
                app.costume_click_zones["new-costume"] = ((.2, .3, .4, .5), (0, 0, 1, 1))
                app.root.winfo_x.return_value = 400 + index * 100
                app.root.winfo_y.return_value = 500 + index * 100
                app.root.winfo_width.return_value = 400
                app.root.winfo_height.return_value = 200
                app.is_flipped = app.is_gravity_flipped = True
                self.assertEqual(callbacks[index], app._spawn_floating_heart)
                heart = self.spawn(app, jitter=jitter, callback=callbacks[index])
                x = int(400 + index * 100 + .7 * 400 - 15 + jitter)
                y = int(500 + index * 100 + .7 * 200 - 22)
                self.assertEqual(heart.geometry.call_args_list[0].args[0],
                                 f"30x30+{x}+{y}")
