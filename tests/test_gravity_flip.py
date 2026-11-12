"""Regression coverage for upstream 5.3.0's independent vertical flip."""
import ast
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import Mock, patch
from PIL import Image
from core.companion import PulchraDesktopCompanion
import test_shortcut_config as config_tests

ROOT = Path(__file__).resolve().parents[1]


class GravityFlipTests(unittest.TestCase):
    def test_saved_flag_round_trip_and_old_profile_default(self):
        with tempfile.TemporaryDirectory() as directory:
            for enabled in (True, False):
                app = config_tests.ShortcutConfigTests().make_companion(directory)
                app.is_gravity_flipped = enabled
                app.head_shortcut_setting = "chat"
                app.save_config_profile()
                self.assertEqual(json.loads((Path(directory) / "config.json").read_text())["gravity_flipped"], enabled)
                reader = config_tests.ShortcutConfigTests().make_companion(directory)
                reader.load_config_profile()
                self.assertEqual(reader.is_gravity_flipped, enabled)
            (Path(directory) / "config.json").write_text("{}")
            reader.is_gravity_flipped = True
            reader.load_config_profile()
            self.assertFalse(reader.is_gravity_flipped)

    def test_toggle_twice_refreshes_image_and_tray_without_mirroring(self):
        app = PulchraDesktopCompanion.__new__(PulchraDesktopCompanion)
        app.root = Mock()
        app.root.after.side_effect = lambda delay, callback: callback()
        app.load_and_scale_image = Mock()
        app.tray_icon = Mock()
        app.is_flipped = True
        app.is_gravity_flipped = False
        app.toggle_gravity_flip()
        self.assertTrue(app.is_gravity_flipped)
        app.toggle_gravity_flip()
        self.assertFalse(app.is_gravity_flipped)
        self.assertTrue(app.is_flipped)
        self.assertEqual(app.load_and_scale_image.call_count, 2)
        self.assertEqual(app.tray_icon.update_menu.call_count, 2)
        del app.tray_icon
        app.toggle_gravity_flip()  # Linux/macOS have no tray.

    def test_head_and_tail_hitboxes_follow_both_axes(self):
        for vertical in (False, True):
            for horizontal in (False, True):
                for name, x, y in (("head", .2, .15), ("tail", .7, .8)):
                    with self.subTest(vertical=vertical, horizontal=horizontal, zone=name):
                        app = PulchraDesktopCompanion.__new__(PulchraDesktopCompanion)
                        app.root = Mock()
                        app.root.winfo_width.return_value = app.root.winfo_height.return_value = 100
                        app.is_click_through = False
                        app.is_flipped = horizontal
                        app.is_gravity_flipped = vertical
                        app.current_image_filename = "test"
                        app.costume_click_zones = {"test": ((.1,.1,.3,.2),(.6,.7,.8,.9))}
                        app.execute_head_shortcut_toggle = Mock()
                        app.process_tail_irritation_tick = Mock()
                        app.start_drag(SimpleNamespace(x=100*(1-x if horizontal else x), y=100*(1-y if vertical else y)))
                        self.assertEqual(app.execute_head_shortcut_toggle.call_count, int(name == "head"))
                        self.assertEqual(app.process_tail_irritation_tick.call_count, int(name == "tail"))

    def test_static_and_walking_pixels_flip_on_both_axes(self):
        # Execute the actual rendering prefix from each method without a desktop.
        source = (ROOT / "core/companion.py").read_text()
        tree = ast.parse(source)
        image = Image.new("RGBA", (2, 2))
        image.putdata([(255,0,0,255),(0,255,0,255),(0,0,255,255),(255,255,0,255)])
        for method, variable in (("load_and_scale_image", "img"), ("_step_glide", "frame_img")):
            node = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == method)
            if method == "load_and_scale_image":
                statements = node.body
                start = next(i for i,n in enumerate(statements) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="img" for t in n.targets))
                statements = statements[start:start+3]
            else:
                block = next(n for n in ast.walk(node) if isinstance(n,ast.If) and isinstance(n.test,ast.Name) and n.test.id=="frames_list")
                statements = block.body[1:4]
            code = compile(ast.Module(body=statements, type_ignores=[]), "<actual-render-prefix>", "exec")
            for vertical in (False, True):
                for horizontal in (False, True):
                    app = SimpleNamespace(is_flipped=horizontal,is_gravity_flipped=vertical)
                    env = {"self":app,"Image":Image,"image_path":"unused","frames_list":[image],"frame_index":0}
                    with patch("PIL.Image.open", return_value=image):
                        exec(code, env)
                    expected=image
                    if horizontal: expected=expected.transpose(Image.FLIP_LEFT_RIGHT)
                    if vertical: expected=expected.transpose(Image.FLIP_TOP_BOTTOM)
                    self.assertEqual(list(env[variable].get_flattened_data()),list(expected.get_flattened_data()))

    def test_controls_and_reset_include_gravity(self):
        source = (ROOT / "core/companion.py").read_text()
        self.assertIn('text="Flip Gravity", command=self.toggle_gravity_flip',source)
        self.assertIn('label="Flip Gravity", command=self.toggle_gravity_flip',source)
        self.assertIn("checked=lambda item: self.is_gravity_flipped",(ROOT/"windows/__init__.py").read_text())
        tree=ast.parse(source)
        reset=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=="reset_dashboard_settings")
        self.assertIn("self.toggle_gravity_flip()",ast.unparse(reset))
