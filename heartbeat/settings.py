import os

from config import OLLAMA_HOST, ROOT_DIR

PROVIDER = os.environ.get('HEARTBEAT_LLM_PROVIDER', 'ollama').lower()
MODEL = os.environ.get('HEARTBEAT_LLM_MODEL', 'qwen3.5:0.8b')
API_BASE = os.environ.get('HEARTBEAT_LLM_API_BASE', OLLAMA_HOST)
INTERVAL = max(1, int(os.environ.get('HEARTBEAT_INTERVAL_SECONDS', '1800')))
TIMEOUT = max(1, int(os.environ.get('HEARTBEAT_TIMEOUT_SECONDS', '120')))
ENABLED = os.environ.get('HEARTBEAT_ENABLED', 'true').lower() == 'true'
PATH = ROOT_DIR / '.a1-heartbeat.json'
