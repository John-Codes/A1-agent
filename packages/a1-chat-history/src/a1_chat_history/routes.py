from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import JSONResponse, PlainTextResponse

from .models import (
    FeedbackIn,
    GeneratedTitleAndSummary,
    MessageIn,
    MessageOut,
    SessionIn,
    SessionOut,
    ToolCallIn,
    UpdateChatSessionRequest,
)
from .xml_tool import run_chat_history_xml_action


def tool_token_middleware(token):
    async def _middleware(request: Request, call_next):
        if request.url.path == "/health" or not token:
            return await call_next(request)
        if request.headers.get("X-Tool-Token") == token:
            return await call_next(request)
        return JSONResponse({"detail": "invalid tool token"}, status_code=401)

    return _middleware


def build_routes(store):
    router = APIRouter()

    @router.get("/sessions", response_model=list[SessionOut])
    def sessions(
        client_id: str | None = None,
        user_id: str | None = None,
        agent_type: str | None = None,
        agent_id: str | None = None,
        workspace_id: str | None = None,
    ):
        return store.sessions(client_id, user_id, agent_type, agent_id, workspace_id)

    @router.post("/sessions", response_model=SessionOut, status_code=201)
    def create_session(item: SessionIn):
        return store.create_session(item)

    @router.patch("/sessions/{session_id}", response_model=SessionOut)
    def update_chat_session(session_id: str, item: UpdateChatSessionRequest):
        session = store.update_chat_session(session_id, item)
        if session is None:
            raise HTTPException(status_code=404, detail="session not found")
        return session

    @router.delete("/sessions/{session_id}", status_code=204)
    def delete_session(session_id: str):
        store.delete_session(session_id)
        return Response(status_code=204)

    @router.get("/sessions/{session_id}/messages", response_model=list[MessageOut])
    def messages(session_id: str, workspace_id: str | None = None):
        return store.messages(session_id, workspace_id)

    @router.post("/sessions/{session_id}/messages", response_model=MessageOut, status_code=201)
    def add_message(session_id: str, item: MessageIn):
        return store.add_message(session_id, item)

    @router.delete("/sessions/{session_id}/messages", status_code=204)
    def clear_messages(session_id: str):
        store.clear_messages(session_id)
        return Response(status_code=204)

    @router.delete("/sessions/{session_id}/messages/{message_id}", status_code=204)
    def delete_message(session_id: str, message_id: str):
        store.delete_message(session_id, message_id)
        return Response(status_code=204)

    @router.patch("/sessions/{session_id}/messages/{message_id}/feedback", response_model=MessageOut)
    def set_feedback(session_id: str, message_id: str, item: FeedbackIn):
        message = store.set_feedback(session_id, message_id, item.feedback)
        if message is None:
            raise HTTPException(status_code=404, detail="message not found")
        return message

    @router.post("/sessions/{session_id}/generated-title-and-summary", response_model=SessionOut)
    def save_generated_title_and_summary(session_id: str, generated: GeneratedTitleAndSummary):
        session = store.save_generated_title_and_summary(session_id, generated)
        if session is None:
            raise HTTPException(status_code=404, detail="session not found")
        return session

    @router.post("/tools/chat_history_api", response_class=PlainTextResponse)
    def chat_history_xml_tool(item: ToolCallIn):
        return run_chat_history_xml_action(store, item.body)

    return router
