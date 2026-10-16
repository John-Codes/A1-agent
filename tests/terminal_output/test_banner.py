import unittest

from features.terminal_output.banner import startup, tool_block, tools_panel
from features.terminal_output import input_prompt, render


NAMES = ["browser_use", "daily_seo", "shell"]
HELP = "/seo status                     Show progress\nDrafts stay local."


class BannerTests(unittest.TestCase):
    def test_plain_startup_keeps_commands_tools_and_seo(self):
        output = startup(NAMES, HELP, False)
        self.assertIn("Personal AI Gateway", output)
        self.assertIn("/markdown", output)
        self.assertIn("browser_use", output)
        self.assertIn("/seo status", output)
        self.assertNotIn("\033[", output)

    def test_color_startup_is_a_panel(self):
        output = startup(NAMES, HELP, True)
        self.assertIn("\033[", output)
        self.assertIn("browser_use", output)
        self.assertIn("/markdown demo", output)
        self.assertIn("Show progress", output)
        self.assertNotIn("##", output)

    def test_tools_panel_plain_is_one_name_per_line(self):
        self.assertEqual(tools_panel(NAMES, False), "browser_use\ndaily_seo\nshell")

    def test_tools_panel_color_names_each_tool(self):
        output = tools_panel(NAMES, True)
        self.assertIn("\033[", output)
        for name in NAMES:
            self.assertIn(name, output)

    def test_tool_result_panel_keeps_body(self):
        plain = render({"kind": "tool", "name": "shell", "response": "ok"}, False)
        self.assertEqual(plain, "DATA: ok")
        colored = tool_block("shell", '{"ok": true}', True)
        self.assertIn("shell", colored)
        self.assertIn("ok", colored)
        self.assertIn("\033[", colored)

    def test_color_prompt_is_marked(self):
        self.assertEqual(input_prompt(False), "YOU: ")
        self.assertIn("YOU", input_prompt(True))
        self.assertIn("\033[", input_prompt(True))
