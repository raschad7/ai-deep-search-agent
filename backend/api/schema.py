from pydantic import BaseModel
from typing import List, Optional


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    query: str
    history: List[Message] = [] 

class ChatResponse(BaseModel):
    reply: str
    router_decision: str