import requests

from config import CHAT_HISTORY_API_TOKEN, CHAT_HISTORY_API_URL, CHAT_HISTORY_TIMEOUT


class ChatHistoryClient:
    def __init__(self, base_url=CHAT_HISTORY_API_URL):
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
        if CHAT_HISTORY_API_TOKEN:
            kwargs.setdefault("headers", {})["X-Tool-Token"] = CHAT_HISTORY_API_TOKEN
        try:
            response = requests.request(
                method,
                f"{self.base_url}{path}",
                timeout=CHAT_HISTORY_TIMEOUT,
                **kwargs,
            )
        except requests.Timeout as exc:
            return {"ok": False, "error_code": "timeout", "body": str(exc)}
        except requests.ConnectionError as exc:
            return {"ok": False, "error_code": "connection_error", "body": str(exc)}
        except requests.RequestException as exc:
            return {"ok": False, "error_code": "request_error", "body": str(exc)}

        body = None
        if response.content:
            try:
                body = response.json()
            except ValueError:
                body = response.text
        return {
            "ok": response.status_code < 400,
            "status_code": response.status_code,
            "body": body,
        }
