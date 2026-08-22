import unittest
from unittest.mock import patch

from tools.trello_clone_agent_friendly_xml.actions import (
    TOOL_PATH,
    run_trello_clone_agent_friendly_xml,
)


class FakeClient:
    sent_path = ""
    sent_payload = {}
    response = {"ok": True, "body": "<trello_clone_result></trello_clone_result>"}

    def post(self, path, payload):
        FakeClient.sent_path = path
        FakeClient.sent_payload = payload
        return FakeClient.response


class TrelloCloneAgentFriendlyXmlTests(unittest.TestCase):
    def test_forwards_body(self):
        FakeClient.response = "<trello_clone_result></trello_clone_result>"

        with patch("tools.trello_clone_agent_friendly_xml.actions.TrelloCloneClient", FakeClient):
            result = run_trello_clone_agent_friendly_xml("<action>menu</action>")

        self.assertEqual(FakeClient.sent_path, TOOL_PATH)
        self.assertEqual(FakeClient.sent_payload, {"body": "<action>menu</action>"})
        self.assertTrue(result.startswith("<trello_clone_result>"))

    def test_forwards_wrapped_body(self):
        FakeClient.response = {"ok": True, "body": "<trello_clone_result></trello_clone_result>"}

        with patch("tools.trello_clone_agent_friendly_xml.actions.TrelloCloneClient", FakeClient):
            result = run_trello_clone_agent_friendly_xml("<action>menu</action>")

        self.assertTrue(result.startswith("<trello_clone_result>"))

    def test_formats_remote_error(self):
        FakeClient.response = {"ok": False, "error_code": "timeout", "body": "too slow"}

        with patch("tools.trello_clone_agent_friendly_xml.actions.TrelloCloneClient", FakeClient):
            result = run_trello_clone_agent_friendly_xml("<action>menu</action>")

        self.assertIn("<ok>false</ok>", result)
        self.assertIn("<error_code>timeout</error_code>", result)


if __name__ == "__main__":
    unittest.main()
