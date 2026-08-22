# AOne Hermes ADHD

Standalone console AI gateway for fast, low-friction work loops.

## Run Locally

From the project folder:

```bash
./run.sh
```

The launcher creates `.venv`, installs `requirements.txt`, and runs `main.py`.
After the first setup, dependencies reinstall only when `requirements.txt`
changes.

## Run API Mode

```bash
./run.sh --api
```

API mode starts FastAPI on `127.0.0.1:8000`.

Core endpoints:

- `GET /health`
- `GET /tools`
- `POST /message` with `{"text":"hello"}`
- `POST /command` with `{"text":"/tools"}`
- `POST /tool` with `{"name":"web_search","body":"latest AI news"}`
- `POST /tick`
- `POST /search` with `{"query":"latest AI news"}`
- `GET /memory`
- `GET /log`

## Run API With Docker

Docker is the recommended API deployment path:

```bash
./docker-run-api.sh
```

The helper builds the `hermes` image, reads `.env`, exposes port `8000`, and
mounts `context/`, `.lancedb/`, and `gateway.log` for persistence.

Manual Docker API run:

```bash
docker build -t hermes .
docker run --rm --env-file .env -p 8000:8000 hermes
```

Optional Docker CLI:

```bash
docker run --rm -it --env-file .env hermes python main.py cli
```

## Install The `Aone` Command

```bash
git clone <repo-url>
cd A1
./install-command.sh
```

Then open a new terminal and run:

```bash
Aone
```

The installer writes a launcher to `~/.local/bin/Aone`, adds `~/.local/bin` to
your shell profile, and sets `POCKETFLOW_GATEWAY_DIR` to this project folder.

To choose a different command name:

```bash
./install-command.sh MyCommand
```

## Configuration

Copy `.env.sample` to `.env` and adjust values for your machine.

Important defaults live in `config.py`:

- `OLLAMA_URL`: text generation endpoint.
- `OLLAMA_MODEL`: chat/generation model.
- `OLLAMA_EMBED_URL`: embedding endpoint.
- `OLLAMA_EMBED_MODEL`: embedding model, default `embeddinggemma`.
- `LANCEDB_PATH`: local semantic memory path, default `.lancedb`.

## Memory Tools

- `memory_store`: store text, document metadata, or captioned photo metadata.
- `memory_search`: semantic search over stored memories.
- `memory_ingest_path`: ingest `.txt`, `.md`, or `.pdf`.
- `rag_sync`: refresh always-on RAG from `context/*.md` and Trello Clone data.

Use `/rag_sync` in CLI/API command mode to force a refresh. Normal messages
trigger a best-effort background refresh when RAG is stale.

## Chat History Auto Save

AOne owns chat session tracking. `chat_history_auto_save.py` creates the active
chat session through the chat history XML tool, stores
`chat_history_session_id` in shared state, and saves each user/assistant turn.

The chat history API owns storage and XML behavior. AOne should keep only the
thin HTTP client, the LLM-callable wrapper, and the auto-save code. Set
`CHAT_HISTORY_API_URL=http://127.0.0.1:8004`,
`CHAT_HISTORY_WORKSPACE_ID=aone-local`, and optionally
`CHAT_HISTORY_API_TOKEN` when the API requires `X-Tool-Token`.

## Project Rule

Code files stay under 100 lines. Keep changes small, direct, and easy to scan.

## Thor Deployment

Thor runs AOne in Docker without changing host CUDA, JetPack, or OS packages:

```bash
./deploy/build_thor_image.sh
./deploy/run_thor_container.sh
./deploy/install_user_service.sh
curl http://100.91.34.26:8001/health
```
