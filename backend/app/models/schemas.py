from pydantic import BaseModel, EmailStr
from typing import Optional

class SubscribeRequest(BaseModel):
    email: EmailStr

class SubscribeResponse(BaseModel):
    message: str

class SubscriberData(BaseModel):
    id: Optional[int]
    email: str
    created_at: str
