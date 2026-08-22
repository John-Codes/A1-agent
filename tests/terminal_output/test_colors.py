import unittest

from features.terminal_output.colors import color_enabled, paint


class FakeStream:
    def __init__(self, tty):
        self.tty = tty

    def isatty(self):
        return self.tty


class ColorTests(unittest.TestCase):
    def test_color_requires_tty(self):
        self.assertTrue(color_enabled(FakeStream(True), {}))
        self.assertFalse(color_enabled(FakeStream(False), {}))

    def test_no_color_disables_color(self):
        self.assertFalse(color_enabled(FakeStream(True), {"NO_COLOR": "1"}))

    def test_paint_can_emit_or_skip_ansi_codes(self):
        self.assertEqual(paint("INFO:", "blue", False), "INFO:")
        self.assertEqual(paint("INFO:", "blue", True), "\033[34mINFO:\033[0m")
