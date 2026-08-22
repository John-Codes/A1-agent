import base64
import binascii

from pydantic import BaseModel, field_validator

MAX_IMAGE_BYTES = 5 * 1024 * 1024


class TextBody(BaseModel):
    text: str = ""
    model_name: str = ""
    api_key: str = ""
    image_data: str = ""
    session_id: str = ""
    user_message: str = ""

    @field_validator("image_data")
    @classmethod
    def validate_image(cls, value):
        if not value:
            return value
        try:
            decoded = base64.b64decode(value, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ValueError("image_data must be valid base64") from exc
        if len(decoded) > MAX_IMAGE_BYTES:
            raise ValueError("image_data exceeds the 5 MB limit")
        return value


class ToolBody(BaseModel):
    name: str
    body: str = ""


class SearchBody(BaseModel):
    query: str = ""
