# a1-chat-history

Self-hosted conversation history API for A1 agents. One command, zero external
services required.

## Install (from the A1-agent repo)

```bash
pip install ./packages/a1-chat-history[mongo]
```

## Run

```bash
a1-chat-history --port 8004
```

That's it. Storage resolves automatically:

| Flag | Behavior |
|---|---|
| *(default)* `--storage auto` | MongoDB if reachable, otherwise a local JSON file |
| `--storage json` | JSON file only (zero dependencies) |
| `--storage mongo` | Require MongoDB; start one automatically with `--auto-mongo` if a `mongod` binary exists |

The default MongoDB backend uses `pymongo` (installed by the `[mongo]` extra)
against `mongodb://127.0.0.1:27017`, database `a1_chat_history`. With
`--auto-mongo`, the service launches a dedicated local `mongod`
(`--dbpath ~/.local/share/a1-chat-history/mongo`) and keeps it out of your way.

## Configuration (env or CLI flags)

| Env | Flag | Default |
|---|---|---|
| `A1_HISTORY_HOST` | `--host` | `127.0.0.1` |
| `A1_HISTORY_PORT` | `--port` | `8004` |
| `A1_HISTORY_STORAGE` | `--storage` | `auto` |
| `A1_HISTORY_DATA_FILE` | `--data-file` | `~/.local/share/a1-chat-history/history.json` |
| `A1_HISTORY_MONGO_URI` | `--mongo-uri` | `mongodb://127.0.0.1:27017` |
| `A1_HISTORY_MONGO_DB` | `--mongo-db` | `a1_chat_history` |
| `A1_HISTORY_AUTO_MONGO` | `--auto-mongo` | off |
| `A1_HISTORY_TOKEN` | `--token` | *(unset — open API)* |

## A1 wiring

A1 already speaks this API. In `A1-agent/.env`:

```
CHAT_HISTORY_API_URL=http://127.0.0.1:8004
```

The API is a drop-in replacement for the previous standalone
`agent_chat_history_api` service (same endpoints, same XML tool contract, same
`X-Tool-Token` header behavior).

## API surface

- `GET /health`
- `GET|POST /sessions`, `PATCH|DELETE /sessions/{id}`
- `GET|POST|DELETE /sessions/{id}/messages`, `DELETE /sessions/{id}/messages/{message_id}`
- `PATCH /sessions/{id}/messages/{message_id}/feedback`
- `POST /sessions/{id}/generated-title-and-summary`
- `POST /tools/chat_history_api` — the XML action tool agents use
  (`create_session`, `add_message`, `list_messages`, `set_feedback`, ...)
