from enum import Enum

class ChatUserType(str, Enum):
    AI = 'AI'
    HUMAN = 'HUMAN'