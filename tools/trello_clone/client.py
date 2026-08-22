import json

import requests

from config import TRELLO_CLONE_API_KEY, TRELLO_CLONE_API_URL, TRELLO_CLONE_TIMEOUT


class TrelloCloneClient:
    def __init__(self, base_url=TRELLO_CLONE_API_URL):
        self.base_url = base_url.rstrip("/")

    def get(self, path, params=None):
        return self._request("GET", path, params=params)

    def post(self, path, payload):
        return self._request("POST", path, json=payload)

    def patch(self, path, payload):
        return self._request("PATCH", path, json=payload)

    def delete(self, path):
        return self._request("DELETE", path)

    def _request(self, method, path, **kwargs):
        if TRELLO_CLONE_API_KEY:
            kwargs.setdefault("headers", {})["x-api-key"] = TRELLO_CLONE_API_KEY
        try:
            response = requests.request(
                method,
                f"{self.base_url}{path}",
                timeout=TRELLO_CLONE_TIMEOUT,
                **kwargs,
            )
        except requests.Timeout as exc:
            return {"ok": False, "error_code": "timeout", "body": str(exc)}
        except requests.ConnectionError as exc:
            return {"ok": False, "error_code": "connection_error", "body": str(exc)}
        except requests.RequestException as exc:
            return {"ok": False, "error_code": "request_error", "body": str(exc)}
        if response.status_code == 204:
            return {"status_code": 204, "ok": True}
        try:
            body = response.json()
        except ValueError:
            body = response.text
        if response.status_code >= 400:
            return {"status_code": response.status_code, "ok": False, "body": body}
        return body


def dumps(result):
    return json.dumps(result, indent=2, sort_keys=True)
