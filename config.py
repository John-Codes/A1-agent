import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
REPO_DIR = ROOT_DIR

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT_DIR / ".env")
except ImportError:
    pass

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", OLLAMA_URL.rsplit("/", 2)[0])
os.environ.setdefault("OLLAMA_HOST", OLLAMA_HOST)
OLLAMA_EMBED_URL = os.environ.get(
    "OLLAMA_EMBED_URL",
    OLLAMA_URL.rsplit("/", 1)[0] + "/embed",
)
OLLAMA_EMBED_MODEL = os.environ.get("OLLAMA_EMBED_MODEL", "embeddinggemma")
DEFAULT_EMBEDDING_PROVIDER = os.environ.get("DEFAULT_EMBEDDING_PROVIDER", "ollama")
DEFAULT_EMBEDDING_MODEL = os.environ.get("DEFAULT_EMBEDDING_MODEL", OLLAMA_EMBED_MODEL)
DEFAULT_EMBEDDING_API_BASE = os.environ.get("DEFAULT_EMBEDDING_API_BASE", OLLAMA_HOST)
FALLBACK_EMBEDDING_PROVIDER = os.environ.get("FALLBACK_EMBEDDING_PROVIDER", "ollama")
FALLBACK_EMBEDDING_MODEL = os.environ.get("FALLBACK_EMBEDDING_MODEL", "")
FALLBACK_EMBEDDING_API_BASE = os.environ.get("FALLBACK_EMBEDDING_API_BASE", "")
_llm_default = (os.environ.get("LLM_DEFAULT", "").split("|") + ["", "", ""])[:3]
DEFAULT_LLM_PROVIDER = (
    _llm_default[0] or os.environ.get("DEFAULT_LLM_PROVIDER", "ollama")
).lower()
DEFAULT_LLM_MODEL = (
    _llm_default[1] or os.environ.get("DEFAULT_LLM_MODEL", "qwen3-vl:32b")
)
DEFAULT_LLM_API_BASE = (
    _llm_default[2] or os.environ.get("DEFAULT_LLM_API_BASE", OLLAMA_HOST)
)
OLLAMA_MODEL = DEFAULT_LLM_MODEL
LITELLM_ENABLED = os.environ.get("LITELLM_ENABLED", "true").lower() == "true"
LLM_GENERATION_TIMEOUT = int(os.environ.get("LLM_GENERATION_TIMEOUT", "120"))
LLM_HEALTHCHECK_TIMEOUT = int(os.environ.get("LLM_HEALTHCHECK_TIMEOUT", "8"))
AONE_MODEL_CONTEXT = int(os.environ.get("AONE_MODEL_CONTEXT", "32768"))
REQUEST_TIMEOUT = int(os.environ.get("REQUEST_TIMEOUT", str(LLM_GENERATION_TIMEOUT)))
EMBEDDING_TIMEOUT = int(os.environ.get("EMBEDDING_TIMEOUT", str(REQUEST_TIMEOUT)))
TOOL_ROUNDS = int(os.environ.get("TOOL_ROUNDS", "3"))
SHELL_TIMEOUT = int(os.environ.get("SHELL_TIMEOUT", "10"))
SHELL_WORKDIR = REPO_DIR
WEB_SEARCH_TIMEOUT = int(os.environ.get("WEB_SEARCH_TIMEOUT", "10"))
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")
TAVILY_SEARCH_URL = "https://api.tavily.com/search"
BING_SEARCH_URL = "https://www.bing.com/search"
BING_NEWS_URL = "https://www.bing.com/news/search"
AGENTMAIL_API_KEY = os.environ.get("AGENTMAIL_API_KEY", "")
AGENTMAIL_API_URL = os.environ.get("AGENTMAIL_API_URL", "https://api.agentmail.to/v0")
AGENTMAIL_TIMEOUT = int(os.environ.get("AGENTMAIL_TIMEOUT", "20"))
BROWSER_USE_OLLAMA_MODEL = os.environ.get("BROWSER_USE_OLLAMA_MODEL", DEFAULT_LLM_MODEL)
BROWSER_USE_HEADLESS = os.environ.get("BROWSER_USE_HEADLESS", "true").lower() == "true"
BROWSER_USE_CHROMIUM_SANDBOX = os.environ.get("BROWSER_USE_CHROMIUM_SANDBOX", "false").lower() == "true"
BROWSER_USE_MAX_STEPS = int(os.environ.get("BROWSER_USE_MAX_STEPS", "30"))
BROWSER_USE_TIMEOUT = int(os.environ.get("BROWSER_USE_TIMEOUT", "300"))
BROWSER_USE_HOME = Path(os.environ.get("BROWSER_USE_HOME", ROOT_DIR / ".browser-use"))
BROWSER_USE_CONFIG_DIR = Path(os.environ.get("BROWSER_USE_CONFIG_DIR", ROOT_DIR / ".browseruse"))
BROWSER_USE_CHROMIUM_EXECUTABLE = os.environ.get(
    "BROWSER_USE_CHROMIUM_EXECUTABLE",
    str(Path.home() / ".cache" / "ms-playwright" / "chromium_headless_shell-1234" / "chrome-linux" / "headless_shell")
)
os.environ.setdefault("BROWSER_USE_HOME", str(BROWSER_USE_HOME))
os.environ.setdefault("BROWSER_USE_CONFIG_DIR", str(BROWSER_USE_CONFIG_DIR))
os.environ.setdefault("PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD", "1")
TRELLO_CLONE_API_URL = os.environ.get(
    "TRELLO_CLONE_API_URL",
    "https://trello-clone-api-latest-2.onrender.com",
)
TRELLO_CLONE_TIMEOUT = int(os.environ.get("TRELLO_CLONE_TIMEOUT", "20"))
TRELLO_CLONE_API_KEY = os.environ.get("TRELLO_CLONE_API_KEY", "")
CHAT_HISTORY_API_URL = os.environ.get("CHAT_HISTORY_API_URL", "http://127.0.0.1:8004")
CHAT_HISTORY_TIMEOUT = int(os.environ.get("CHAT_HISTORY_TIMEOUT", "2"))
CHAT_SUMMARY_DELAY = int(os.environ.get("CHAT_SUMMARY_DELAY", "180"))
CHAT_HISTORY_SESSION_TITLE = os.environ.get("CHAT_HISTORY_SESSION_TITLE", "AOne Hermes ADHD")
CHAT_HISTORY_WORKSPACE_ID = os.environ.get("CHAT_HISTORY_WORKSPACE_ID", "aone-local")
CHAT_HISTORY_API_TOKEN = os.environ.get("CHAT_HISTORY_API_TOKEN", "")

TICK_INTERVAL_SECONDS = int(os.environ.get("HEARTBEAT_INTERVAL_SECONDS", "1800"))
LOG_PATH = ROOT_DIR / "gateway.log"
LANCEDB_PATH = Path(os.environ.get("LANCEDB_PATH", ROOT_DIR / ".lancedb"))
LANCEDB_TABLE = os.environ.get("LANCEDB_TABLE", "memory")

CONTEXT_DIR = ROOT_DIR / "context"
SOUL_PATH = CONTEXT_DIR / "SOUL.md"
AGENTS_PATH = CONTEXT_DIR / "AGENTS.md"
MEMORY_PATH = CONTEXT_DIR / "MEMORY.md"
TOOLS_PATH = CONTEXT_DIR / "TOOLS.md"
LIFE_LOG_PATH = CONTEXT_DIR / "LIFE_LOG.xml"

LIFE_IDEA_LOG_API_URL = os.environ.get("LIFE_IDEA_LOG_API_URL", "http://127.0.0.1:8010")
LIFE_IDEA_LOG_TIMEOUT = int(os.environ.get("LIFE_IDEA_LOG_TIMEOUT", "20"))
