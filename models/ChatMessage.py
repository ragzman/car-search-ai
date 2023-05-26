from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder

# Create a data model using Pydantic
class ChatMessage(BaseModel):
    userType: str
    text: str

    def __init__(self, userType: str, text: str, **kwargs):
        super().__init__(userType=userType, text=text, **kwargs)
    
    def json(self):
        return jsonable_encoder(self)