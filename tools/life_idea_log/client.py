import requests

from config import LIFE_IDEA_LOG_API_URL, LIFE_IDEA_LOG_TIMEOUT


class LifeIdeaLogClient:
    def __init__(self, base_url=LIFE_IDEA_LOG_API_URL):
        self.base_url = base_url.rstrip("/")

    def health(self):
        return self._request("GET", "/health")

    def create(self, payload):
        return self._request("POST", "/entries", json=payload)

    def list(self, params):
        return self._request("GET", "/entries", params=params)

    def get(self, entry_id):
        return self._request("GET", f"/entries/{entry_id}")

    def update(self, entry_id, payload):
        return self._request("PUT", f"/entries/{entry_id}", json=payload)

    def delete(self, entry_id):
        return self._request("DELETE", f"/entries/{entry_id}")

    def _request(self, method, path, **kwargs):
        response = requests.request(
            method,
            f"{self.base_url}{path}",
            timeout=LIFE_IDEA_LOG_TIMEOUT,
            **kwargs,
        )
        if response.status_code == 204:
            return {"ok": True}
        try:
            body = response.json()
        except ValueError:
            body = response.text
        if response.status_code >= 400:
            return {"ok": False, "status_code": response.status_code, "body": body}
        return body
