"""Schemas for the chat app."""
from pydantic import BaseModel, validator
import json
from enum import Enum


class MessageType(Enum):
    STREAM_START = "STREAM_START"
    STREAM_END = "STREAM_END"
    STREAM_MSG = "STREAM_MSG"
    COMMAND = "COMMAND"
    CLIENT_QUESTION = "CLIENT_QUESTION"

    def __str__(self):
        return self.value


class MessageSender(Enum):
    HUMAN = "HUMAN"
    AI = "AI"

    def __str__(self):
        return self.value


class ChatMessage(BaseModel):
    """Chat Message schema."""

    sender: MessageSender
    message: str
    type: MessageType

    def toJson(self):
        return json.dumps(self.dict(), cls = EnumEncoder)
    

class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return str(obj)
        return super().default(obj)

    
