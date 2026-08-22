from urllib.parse import quote

import requests

from config import AGENTMAIL_API_KEY, AGENTMAIL_API_URL, AGENTMAIL_TIMEOUT


class AgentMailClient:
    def __init__(self, api_key=None, base_url=None, timeout=None):
        self.api_key = api_key or AGENTMAIL_API_KEY
        self.base_url = (base_url or AGENTMAIL_API_URL).rstrip("/")
        self.timeout = timeout or AGENTMAIL_TIMEOUT
        if not self.api_key:
            raise ValueError("AGENTMAIL_API_KEY is not set")

    def create_inbox(self, payload):
        return self._request("POST", "/inboxes", json=payload)

    def list_inboxes(self, params):
        return self._request("GET", "/inboxes", params=params)

    def get_inbox(self, inbox_id):
        return self._request("GET", f"/inboxes/{_path(inbox_id)}")

    def send(self, inbox_id, payload):
        path = f"/inboxes/{_path(inbox_id)}/messages/send"
        return self._request("POST", path, json=payload)

    def list_messages(self, inbox_id, params):
        return self._request("GET", f"/inboxes/{_path(inbox_id)}/messages", params=params)

    def get_message(self, inbox_id, message_id):
        path = f"/inboxes/{_path(inbox_id)}/messages/{_path(message_id)}"
        return self._request("GET", path)

    def reply(self, inbox_id, message_id, payload):
        path = f"/inboxes/{_path(inbox_id)}/messages/{_path(message_id)}/reply"
        return self._request("POST", path, json=payload)

    def update_message(self, inbox_id, message_id, payload):
        path = f"/inboxes/{_path(inbox_id)}/messages/{_path(message_id)}"
        return self._request("PATCH", path, json=payload)

    def _request(self, method, path, **kwargs):
        response = requests.request(
            method,
            f"{self.base_url}{path}",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=self.timeout,
            **kwargs,
        )
        if response.status_code >= 400:
            raise RuntimeError(f"AgentMail {response.status_code}: {response.text[:500]}")
        if not response.content:
            return {}
        return response.json()


def _path(value):
    return quote(str(value), safe="")
