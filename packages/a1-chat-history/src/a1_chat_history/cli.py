import argparse

import uvicorn

from .app import create_app
from .settings import Settings
from .stores import get_store


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="a1-chat-history",
        description="Self-hosted conversation history API for A1 agents "
        "(JSON storage by default, optional local MongoDB).",
    )
    parser.add_argument("--host", help="Bind host (default 127.0.0.1, env A1_HISTORY_HOST)")
    parser.add_argument("--port", type=int, help="Bind port (default 8004, env A1_HISTORY_PORT)")
    parser.add_argument(
        "--storage", choices=("auto", "json", "mongo"),
        help="auto: MongoDB if reachable, else JSON (default, env A1_HISTORY_STORAGE)",
    )
    parser.add_argument("--data-file", help="JSON storage path (env A1_HISTORY_DATA_FILE)")
    parser.add_argument("--mongo-uri", help="MongoDB URI (env A1_HISTORY_MONGO_URI)")
    parser.add_argument("--mongo-db", help="MongoDB database name (env A1_HISTORY_MONGO_DB)")
    parser.add_argument(
        "--auto-mongo", action="store_true",
        help="Start a dedicated local mongod when MongoDB is unreachable (env A1_HISTORY_AUTO_MONGO)",
    )
    parser.add_argument("--token", help="Require X-Tool-Token header on writes (env A1_HISTORY_TOKEN)")
    args = parser.parse_args(argv)

    settings = Settings.from_env()
    if args.host is not None:
        settings.host = args.host
    if args.port is not None:
        settings.port = args.port
    if args.storage is not None:
        settings.storage = args.storage
    if args.data_file is not None:
        settings.data_file = args.data_file
    if args.mongo_uri is not None:
        settings.mongo_uri = args.mongo_uri
    if args.mongo_db is not None:
        settings.mongo_db = args.mongo_db
    if args.auto_mongo:
        settings.auto_start_mongo = True
    if args.token is not None:
        settings.tool_token = args.token

    store, backend = get_store(settings)
    print(f"A1 Chat History API -> http://{settings.host}:{settings.port} (storage: {backend})", flush=True)
    uvicorn.run(create_app(store, settings.tool_token), host=settings.host, port=settings.port, log_level="warning")


if __name__ == "__main__":
    main()
