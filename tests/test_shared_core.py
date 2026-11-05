import ast
import importlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SharedCoreTests(unittest.TestCase):
    def test_assets_are_valid(self):
        from PIL import Image
        for path in (ROOT / "assets").iterdir():
            if path.suffix == ".json":
                json.loads(path.read_text(encoding="utf-8"))
            elif path.suffix in (".png", ".ico"):
                with Image.open(path) as image:
                    image.verify()

    def test_adapter_interface(self):
        # Inspect syntax without importing another OS's native bindings.
        required = {"config_directory", "configure_transparency", "open_folder",
                    "shape_window", "set_click_through", "idle_seconds", "setup_tray"}
        for name in ("windows", "mac", "linux"):
            tree = ast.parse((ROOT / name / "__init__.py").read_text())
            actual = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
            self.assertTrue(required <= actual, name)

    def test_no_windows_native_calls_in_shared_core(self):
        source = (ROOT / "core" / "companion.py").read_text()
        for text in ("ctypes.windll", "os.startfile", '"-transparentcolor"'):
            self.assertNotIn(text, source)
        self.assertIn("gugoxiii ultimatedanx", source)

    def test_asset_lookup_ignores_current_working_directory(self):
        from core.companion import get_asset_path
        self.assertEqual(Path(get_asset_path("pulchra_overlay_standing.png")),
                         ROOT / "assets" / "pulchra_overlay_standing.png")


if __name__ == "__main__":
    unittest.main()
