"""Regression coverage for upstream 5.3.2 settings column alignment."""
import ast
import inspect
import textwrap
import unittest

from core.companion import PulchraDesktopCompanion


class SettingsLayoutTests(unittest.TestCase):
    def test_columns_share_bottom_edge_without_overlapping(self):
        tree = ast.parse(textwrap.dedent(inspect.getsource(
            PulchraDesktopCompanion.open_settings_dashboard)))
        placements = {}
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and
                    isinstance(node.func, ast.Attribute) and
                    node.func.attr == "place" and
                    isinstance(node.func.value, ast.Name)):
                placements[node.func.value.id] = {
                    item.arg: ast.literal_eval(item.value)
                    for item in node.keywords}
        layout = placements["layout_frame"]
        self.assertEqual(layout, dict(x=225, y=275, width=205, height=325))
        for frame in ("mood_frame", "cooldown_frame"):
            self.assertEqual(layout["y"] + layout["height"],
                             placements[frame]["y"] + placements[frame]["height"])
        utilities = placements["util_frame"]
        self.assertLess(utilities["y"] + utilities["height"], layout["y"])
        self.assertLess(placements["mood_frame"]["x"] +
                        placements["mood_frame"]["width"], layout["x"])
        self.assertLess(layout["x"] + layout["width"],
                        placements["cooldown_frame"]["x"])
