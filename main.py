import os
import sys


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "cli"
    if mode in {"--api", "api"}:
        import uvicorn

        host = os.environ.get("HERMES_API_HOST", "127.0.0.1")
        port = int(os.environ.get("HERMES_API_PORT", "8000"))
        uvicorn.run("api:app", host=host, port=port)
        return

    from cli import main as run_cli

    run_cli()


if __name__ == "__main__":
    main()
