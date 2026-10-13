import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import agent
from api_models import SearchBody, TextBody, ToolBody
from commands import run as run_command
from tools import tool_names

from heartbeat.api import lifespan, router as heartbeat_router

app = FastAPI(title="AOne Hermes ADHD API", lifespan=lifespan)
app.include_router(heartbeat_router)

_default_origins = [
    "http://127.0.0.1:3000",
    "http://localhost:3000",
]
_extra_origins = [
    origin.strip()
    for origin in os.environ.get("A1_AGENT_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_default_origins + _extra_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/tools")
def tools():
    return {"tools": tool_names()}


@app.post("/message")
def message(body: TextBody):
    return agent.message(body.text, body.session_id, image_data=body.image_data)


@app.post("/generate")
def generate(body: TextBody):
    result = agent.message(
        body.text,
        body.session_id,
        body.user_message,
        body.image_data,
    )
    return {
        "success": not bool(result.get("error")),
        "response": result.get("response") or "",
        "error": result.get("error"),
    }


@app.post("/command")
def command(body: TextBody):
    return run_command(body.text)


@app.post("/tool")
def tool(body: ToolBody):
    try:
        return {"response": agent.tool(body.name, body.body), "error": None}
    except Exception as exc:
        return {"response": "", "error": str(exc)}


@app.post("/tick")
def tick():
    return agent.tick()


@app.post("/search")
def search(body: SearchBody):
    return tool(ToolBody(name="web_search", body=body.query))


@app.get("/memory")
def memory():
    return {"text": agent.memory()}


@app.get("/log")
def log():
    return {"text": agent.log()}
