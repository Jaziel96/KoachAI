from pydantic import BaseModel, Field


class WhatsAppTextBody(BaseModel):
    body: str


class WhatsAppMessage(BaseModel):
    id: str
    from_: str = Field(alias="from")
    type: str
    text: WhatsAppTextBody | None = None

    model_config = {"populate_by_name": True}


class WhatsAppValue(BaseModel):
    messages: list[WhatsAppMessage] | None = None


class WhatsAppChange(BaseModel):
    value: WhatsAppValue


class WhatsAppEntry(BaseModel):
    changes: list[WhatsAppChange]


class WhatsAppPayload(BaseModel):
    entry: list[WhatsAppEntry]
