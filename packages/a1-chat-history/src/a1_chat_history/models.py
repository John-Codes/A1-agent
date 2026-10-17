from datetime import datetime, timezone

from pydantic import BaseModel, Field, field_validator

from .workspace_ids import clean_workspace_id, default_workspace_id


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class SessionIn(BaseModel):
    workspace_id: str = Field(default_factory=default_workspace_id)
    user_id: str = "local"
    client_id: str = "local"
    agent_type: str = "master"
    model_name: str = "local-agent"
    agent_id: str | None = None
    title: str = "Chat v3"
    summary: str = ""

    @field_validator("workspace_id")
    @classmethod
    def valid_workspace_id(cls, value):
        return clean_workspace_id(value)


class SessionOut(SessionIn):
    id: str
    created_at: str
    updated_at: str


class MessageIn(BaseModel):
    text: str = ""
    mine: bool
    timestamp: str | None = None
    image_data: str | None = None
    has_image: bool = False


class MessageOut(BaseModel):
    id: str
    workspace_id: str = ""
    session_id: str
    text: str = ""
    mine: bool
    timestamp: str = Field(default_factory=now_iso)
    has_image: bool = False
    feedback: str | None = None


class UpdateChatSessionRequest(BaseModel):
    title: str | None = None
    summary: str | None = None


class GeneratedTitleAndSummary(BaseModel):
    title: str = Field(min_length=1, max_length=80)
    summary: str = Field(min_length=1, max_length=500)


class FeedbackIn(BaseModel):
    feedback: str | None = None


class ToolCallIn(BaseModel):
    body: str = ""
