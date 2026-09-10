from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class BlogCreate(BaseModel):
    title: str
    content: str
    category: str
    read_time: str

class BlogResponse(BaseModel):
    id: int
    title: str
    content: str
    category: str
    read_time: str
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True