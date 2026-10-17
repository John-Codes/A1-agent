import os
import unittest
from unittest import mock

from features.terminal_output import render


MARKDOWN = """## Status

**Ready** to review.

- English draft
- Spanish draft
"""


class MarkdownRenderTests(unittest.TestCase):
    def test_short_color_reply_stays_one_line(self):
        result = {"kind": "message", "response": "Hello"}
        self.assertEqual(render(result, True), "\033[36mMasterLLM:\033[0m Hello")

    def test_markdown_body_is_colored_when_enabled(self):
        result = {"kind": "message", "response": MARKDOWN}
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("A1_MARKDOWN", None)
            output = render(result, True)
        self.assertIn("\033[", output)
        self.assertIn("Status", output)
        self.assertNotIn("## Status", output)
        self.assertIn("Ready", output)

    def test_markdown_off_keeps_plain_body(self):
        result = {"kind": "message", "response": MARKDOWN}
        with mock.patch.dict(os.environ, {"A1_MARKDOWN": "0"}):
            output = render(result, True)
        self.assertEqual(output, f"\033[36mMasterLLM:\033[0m {MARKDOWN}")

    def test_no_color_flag_skips_markdown(self):
        result = {"kind": "message", "response": MARKDOWN}
        self.assertEqual(render(result, False), f"MasterLLM: {MARKDOWN}")
