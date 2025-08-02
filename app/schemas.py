import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class ChatRequest(BaseModel):
    message: str

class RefreshRequest(BaseModel):
    refresh_token: str

class MessageOut(BaseModel):
    id: int
    sender: str
    content: str
    created_at: datetime.datetime

    class Config:
        orm_mode = True

class ChatOut(BaseModel):
    id: int
    title: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True

class ChatOutDetail(BaseModel):
    id: int
    title: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    messages: List[MessageOut] = []

    class Config:
        orm_mode = True

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime.datetime
    chats: List[ChatOut] = []

    class Config:
        orm_mode = True

class ChatUpdate(BaseModel):
    title: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None

    class Config:
        orm_mode = True

