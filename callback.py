"""Callback handlers used in the app."""
from typing import Any, Dict, List


from langchain.callbacks.base import AsyncCallbackHandler

from models.schemas import ChatMessage
from models.schemas import MessageType
from models.schemas import MessageSender



class StreamingLLMCallbackHandler(AsyncCallbackHandler):
    """Callback handler for streaming LLM responses."""

    def __init__(self, sid, sio):
        self.sid = sid
        self.sio = sio

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        resp = ChatMessage(sender=MessageSender.AI, message=token, type=MessageType.STREAM_MSG)
        await self.sio.emit('chat', resp.toJson(), room = self.sid)
