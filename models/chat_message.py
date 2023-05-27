from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from models.chat_user_type import ChatUserType

# Create a data model using Pydantic
class ChatMessage(BaseModel):
    userType: ChatUserType
    text: str

    def __init__(self, userType: ChatUserType, text: str, **kwargs):
        super().__init__(userType=userType, text=text, **kwargs)
    
    def json(self):
        return jsonable_encoder(self)
    
