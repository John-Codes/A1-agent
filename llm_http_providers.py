import os
import socket

import requests
import urllib3.util.connection as urllib3_connection

from config import LLM_GENERATION_TIMEOUT
from llm_response import response_text


def call_groq(prompt, model):
    key = _required_key("GROQ_API_KEY")
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.6,
        "max_completion_tokens": 4096,
    }
    response = _post_json(_groq_url(), _auth_headers(key), payload)
    if not response.ok:
        raise requests.HTTPError(f"{response.status_code} Groq error: {response.text[:1000]}")
    return response_text(response, "Groq")


def call_openrouter(prompt, model):
    key = _required_key("OPENROUTER_API_KEY")
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 4096,
    }
    response = _post_json(_openrouter_url(), _auth_headers(key), payload)
    if not response.ok:
        raise requests.HTTPError(f"{response.status_code} OpenRouter error: {response.text[:1000]}")
    return response_text(response, "OpenRouter")


def call_nvidia_nim(prompt, model, api_base):
    key = _required_key("NVIDIA_API_KEY")
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 1,
        "top_p": 0.95,
        "max_tokens": 16384,
        "extra_body": {"chat_template_kwargs": {"thinking": False}},
        "stream": False,
    }
    response = _post_json(f"{api_base.rstrip('/')}/chat/completions", _auth_headers(key), payload)
    if not response.ok:
        raise requests.HTTPError(f"{response.status_code} NVIDIA NIM error: {response.text[:1000]}")
    return response_text(response, "NVIDIA NIM")


def _post_json(url, headers, payload):
    urllib3_connection.allowed_gai_family = lambda: socket.AF_INET
    return requests.post(url, headers=headers, json=payload, timeout=LLM_GENERATION_TIMEOUT)


def _required_key(name):
    key = os.environ.get(name, "")
    if not key:
        raise ValueError(f"{name} is not set.")
    return key


def _auth_headers(key):
    return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}


def _groq_url():
    return "https://api.groq.com/openai/v1/chat/completions"


def _openrouter_url():
    return "https://openrouter.ai/api/v1/chat/completions"
