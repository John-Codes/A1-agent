from unittest.mock import Mock

import pytest

from llm_response import response_text


def response(data):
    return Mock(status_code=200, json=Mock(return_value=data))


def test_success():
    reply = {"choices": [{"message": {"content": "OK"}}]}
    assert response_text(response(reply), "OpenRouter") == "OK"


def test_error_with_http_200_preserves_provider_message():
    reply = {"error": {"code": 429, "message": "Provider temporarily rate limited"}}
    with pytest.raises(RuntimeError, match="429: Provider temporarily rate limited"):
        response_text(response(reply), "OpenRouter")


@pytest.mark.parametrize("reply", [{}, {"choices": []}, {"choices": None}, []])
def test_malformed_response(reply):
    with pytest.raises(ValueError):
        response_text(response(reply), "OpenRouter")


@pytest.mark.parametrize("content", [None, "", "  "])
def test_empty_completion(content):
    with pytest.raises(ValueError, match="empty text completion"):
        response_text(response({"choices": [{"message": {"content": content}}]}), "OpenRouter")
