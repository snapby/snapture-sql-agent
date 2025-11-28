from pydantic import BaseModel

from app.models.graph.interrupts import InterruptPolicy


class ChatModelSettings(BaseModel):
    primary_model: str = "claude-sonnet-4-5"
    secondary_model: str = "claude-opus-4-5"
    max_tokens: int = 32_798


class ChatbotRequest(BaseModel):
    content: str
    interrupt_policy: InterruptPolicy = "never"
    tables_schema_xml: str
    chat_model_settings: ChatModelSettings = ChatModelSettings()


class ChatbotResumeRequest(BaseModel):
    query: str
    reason: str | None = None
    tables_schema_xml: str
    chat_model_settings: ChatModelSettings = ChatModelSettings()
