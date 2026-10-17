from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import build_routes, tool_token_middleware


def create_app(store, tool_token=""):
    app = FastAPI(title="A1 Chat History API")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.middleware("http")(tool_token_middleware(tool_token))
    app.include_router(build_routes(store))

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
