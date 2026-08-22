import unittest

from features.terminal_output import input_prompt, render


class RendererTests(unittest.TestCase):
    def test_master_llm_message_label(self):
        result = {"kind": "message", "speaker": "master_llm", "response": "Hello"}
        self.assertEqual(render(result, False), "MasterLLM: Hello")

    def test_master_llm_thinking_is_labeled_separately(self):
        result = {"kind": "message", "response": "<think>Check facts</think>\nREADY"}
        expected = "MasterLLM[thinking]: Check facts\nMasterLLM: READY"
        self.assertEqual(render(result, False), expected)

    def test_named_and_indexed_sub_llm_labels(self):
        named = {"kind": "message", "speaker": "sub_llm", "speaker_name": "coder", "response": "Done"}
        indexed = {"kind": "message", "speaker": "sub_llm", "speaker_index": 2, "response": "Done"}
        self.assertEqual(render(named, False), "SubLLM[coder]: Done")
        self.assertEqual(render(indexed, False), "SubLLM[2]: Done")

    def test_fallback_warning_precedes_response(self):
        result = {"kind": "message", "response": "Ready", "llm_fallback_used": True}
        expected = "WARNING: MasterLLM fallback used\nMasterLLM: Ready"
        self.assertEqual(render(result, False), expected)

    def test_error_and_data_labels(self):
        self.assertEqual(render({"kind": "error", "error": "bad"}, False), "ERROR: bad")
        data = {"kind": "tool", "response": "raw value"}
        self.assertEqual(render(data, False), "DATA: raw value")

    def test_text_error_prefix_is_normalized(self):
        result = {"kind": "text", "text": "ERROR | model unavailable"}
        self.assertEqual(render(result, False), "ERROR: model unavailable")

    def test_info_and_success_categories(self):
        info = {"kind": "text", "category": "info", "text": "status"}
        success = {"kind": "text", "category": "success", "text": "saved"}
        self.assertEqual(render(info, False), "INFO: status")
        self.assertEqual(render(success, False), "SUCCESS: saved")
        self.assertEqual(render(success, True), "\033[32mSUCCESS:\033[0m saved")

    def test_tick_and_prompt_labels(self):
        tick = {"kind": "tick", "speaker": "master_llm", "response": "reflect"}
        self.assertEqual(render(tick, False), "MasterLLM[tick]: reflect")
        self.assertEqual(input_prompt(False), "YOU: ")

    def test_color_applies_to_label_only(self):
        result = {"kind": "message", "response": "Hello"}
        expected = "\033[36mMasterLLM:\033[0m Hello"
        self.assertEqual(render(result, True), expected)
