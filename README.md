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

Browser automation has separate settings: `BROWSER_USE_PROVIDER` accepts
`ollama` or `openrouter`. OpenRouter uses the default OpenRouter route unless
`BROWSER_USE_MODEL` is set. Ollama uses `BROWSER_USE_OLLAMA_MODEL`.
Set `BROWSER_USE_CHROMIUM_EXECUTABLE` to an installed Chrome/Chromium binary.
`LIFE_LOG_OLLAMA_MODEL` and `CHAT_SUMMARY_OLLAMA_MODEL` select local summary models
independently of the main cloud LLM. Restart the agent after changing `.env`.

Every failed model attempt prints its provider/model and reason to the console,
including failures followed by a successful fallback. Tool failures print
`Tool <name> failed ... Check log for more info @ <absolute log path>`.
Full tool results, provider failures, browser
diagnostics, and tracebacks are saved to `gateway.log`, with configured secrets
redacted. Use `/log` or `tail -n 100 gateway.log` to inspect details.

## Daily SEO inside A1

This workflow prepares content for **CDLTestReady**. The `cdl_articles` tool
can submit drafts and publish authorized content through the article API.
The daily drafting loop does not automatically publish or email its drafts.

Configure `CDL_ARTICLE_API_URL`, `CDL_ARTICLE_WORKSPACE`, and
`CDL_ARTICLE_ADMIN_TOKEN` in `.env`, then restart A1. Run `/cdl_articles {}`
to read the API's current instructions. It supports validate, create, get,
list, update, publish, and delete. Content stays in Markdown; author defaults
to Sergio and creation/update timestamps come from the API.
`/cdl_articles {"action":"publish","slug":"reviewed-article-en"}` publishes
the saved article to the API. The existing website job syncs published content
on its deployment schedule; API success does not mean the website is live yet.
Model tool mutations require execute mode; instructions/list/get are read-only.
Direct `/cdl_articles` console commands are explicit user actions in either mode. See `lib/features/cdl_articles/README.md` for local testing.

Startup displays the available SEO commands and parameters. `/seo help` shows
them again. Author defaults to Sergio; change it with `/seo author <name>` or
the JSON `author` parameter on start/set. Each draft includes author and
`created_at` (date/time with timezone offset) in Markdown frontmatter.

Start A1 in tmux, then type `/seo start 5` to create up to five English/Spanish
article pairs per day (ten Markdown files). `/seo set 2` changes the quota;
`/seo stop` pauses; `/seo status` shows progress. Detach tmux and leave A1 running.
Restart A1 once after installing this change to load the new console runner.
Enabled state survives restart; no separate script or service is required.
Use `/seo title Texas CDL air brakes` to set what this instance writes about. The
`content_title` is saved in Markdown and included in the writing brief. The tmux
window shows the campaign, progress, and current article topic while drafting,
then the generated article title when ready. No console digging required.

The title defines the **content subject**. Set target search phrases separately:

```text
/seo title Texas CDL air brakes
/seo keywords Texas air brakes practice test, air brake inspection checklist
/seo start 2
```

Explicit keywords replace registry selection, producing one bilingual pair per
phrase within the requested subject. Add new phrases when exhausted; A1 avoids
repeating the same subject/phrase. `/seo keywords` clears the override and returns
to the Markdown keyword registry. Both parameters persist in `DAILY_SEO.md`.

Edit `context/DAILY_SEO.md` for the quota and timezone. Manage keywords in
`context/CDL_SEO_KEYWORDS.md` directly or use `/cdl_keywords` with JSON:

```text
/cdl_keywords {"action":"list"}
/cdl_keywords {"action":"create","state":"TX","topic":"Air brakes study planning","english":"Texas air brakes study plan","spanish":"plan de estudio frenos de aire Texas"}
/cdl_keywords {"action":"update","id":"KW-002","priority":"P2"}
/cdl_keywords {"action":"delete","id":"KW-002"}
```

Direct `/cdl_keywords` commands work from the console in either mode. Model tool
mutations still require execution mode. `/seo` explicitly controls the schedule.
Drafts appear under `docs/seo/drafts/YYYY-MM-DD/slot-keyword/`, with `en.md` and
`es.md`. They need human factual review; generation checks are structural only.
No automatic publishing or outgoing review email is enabled. Research uses A1's
web search and writing uses its configured LLM routes.

Progress is saved in `.a1-seo.json`. Each keyword is used once; add new active
topics when the backlog runs out. Failed/interrupted slots consume quota and
are not retried automatically. Status and the progress file show failures.
Quota resets at local midnight; missed days are skipped. Stopping prevents the
next pair and cancels the current worker. An existing emergency stop blocks work.

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


## Plan and Execute in the Terminal

From this project directory, run `./run.sh`, then:

```text
/plan Investigate why the browser tool fails and propose a fix
/status
/execute
```

`/plan <goal>` creates a saved plan with instructions, dependencies, and an
observable completion check for each task. Review it before `/execute`.
A new successful `/plan <goal>` replaces the previous queue. `/plan` without a
goal selects planning without replacing it. After using task commands, ordinary
messages create plans; existing slash commands remain available.

Planning tools are enforced in the dispatcher: only `web_search`, `memory_search`,
and `project_read` are allowed. `project_read` accepts a relative project text
file path, excludes hidden paths and paths outside the project, and returns at
most 16,000 characters. Planning still writes its own local state and diagnostic
logs. Shell and browser tools are excluded from planning because their existing
interfaces cannot guarantee read-only behavior.

`/execute` runs ready tasks sequentially and prints model rounds, tool activity,
results, and task status. Dependencies must finish first. Completion requires the
worker to report a successful check and evidence; this is model-reported evidence,
not an independent correctness guarantee. Missing capabilities or input should
produce a blocked task. Execution retains the existing tools and their restrictions;
it does not add unrestricted shell access or file editing.

**Press Esc during planning or execution for emergency stop.** Ctrl-C also stops
active task work. The controller kills its worker process group and discovered
child processes, including detached browser children. The terminal stays open,
and execution never resumes automatically. Any escape sequence (including arrow
keys) stops work deliberately. This feature requires a Linux interactive terminal;
these task commands are CLI-only and do not change API behavior.

`/status` shows saved work. `/resume` explicitly retries interrupted, blocked, or
failed tasks within their attempt limit, then continues the queue. Inspect external
effects before resuming: stopping cannot undo an already accepted remote request.
The worker is instructed to inspect existing effects before retrying and report
blocked if they cannot be checked. After a crash, running tasks load as interrupted.

State lives in `.a1-tasks.json` in this directory, with atomic saves and owner-only
file permissions. A lock prevents two terminal controllers from executing this
queue at once. State and lock files are ignored by Git. Detailed diagnostics still
use `gateway.log`; activity shown in the console uses the existing secret redaction.

Limits can be set through environment variables (positive integers):

| Variable | Default | Meaning |
| --- | --- | --- |
| `A1_TASK_TOOL_ROUNDS` | 12 | Model/tool rounds per worker |
| `A1_TASK_TIMEOUT` | 600 | Seconds per execution task |
| `A1_RUN_TIMEOUT` | 1800 | Seconds per execution run |
| `A1_TASK_ATTEMPTS` | 3 | Attempts per task, including explicit resumes |

Planning has a 600-second timeout. Three identical tool requests and results stop
a worker as no progress. Reaching a limit or failure preserves unfinished tasks;
it never marks them complete. Blocked dependencies do not busy-loop. Create a new
plan after inspecting a task that has exhausted its attempts.


## Dedicated 30-Minute Heartbeat

CLI and API mode now schedule a heartbeat in the background every 1,800 seconds,
without waiting for terminal input or acquiring the main agent's lock. Each check
runs in its own cancellable worker with separate model state. The default is
`ollama/qwen3.5:0.8b` at `OLLAMA_HOST`. It never falls back to a main model. This model
is reserved: main-agent fallbacks skip it, and selecting it as the main model
reports a configuration error. Configure a different heartbeat model if needed.
The Ollama check disables thinking and limits output to 128 tokens with a 4K
context. A different model on the same server still shares that server's hardware;
use `HEARTBEAT_LLM_API_BASE` for separate compute when required.

The heartbeat reads local context and the saved task queue and reports pending,
running, or blocked work. **It does not plan, execute, resume, or modify tasks.**
The task executor remains controlled by `/plan`, `/execute`, and `/resume`.
`/status` shows task state plus the latest heartbeat report. `/heartbeat` shows
heartbeat status alone; `/tick` requests a background check immediately in the CLI.

Esc at the terminal prompt, or during task planning/execution, cancels the local
heartbeat worker and pauses future checks. `/heartbeat stop` does the same;
`/heartbeat resume` explicitly enables scheduling again. Exiting the CLI stops the
scheduler. The pause lasts for the current application process; restarting starts
scheduling again unless `HEARTBEAT_ENABLED=false`. Requests already accepted by a
remote model server may continue there after local cancellation.

For API clients: `POST /tick` runs an isolated check, `GET /heartbeat/status` shows
its status, and `POST /heartbeat/stop` or `/heartbeat/resume` control that API
process's scheduler. CLI and API processes share a file lock and last-check time
to avoid simultaneous/duplicate scheduled checks, but their pause controls are
local to each process. Run one application instance for one emergency-stop scope.

Set `HEARTBEAT_ENABLED`, `HEARTBEAT_INTERVAL_SECONDS`, `HEARTBEAT_LLM_PROVIDER`,
`HEARTBEAT_LLM_MODEL`, `HEARTBEAT_LLM_API_BASE`, and `HEARTBEAT_TIMEOUT_SECONDS`
in `.env` as needed, then restart. Latest results are saved atomically in the
Git-ignored `.a1-heartbeat.json`. No external tools or memory writes run during a
heartbeat; only its own diagnostic status file is updated.
