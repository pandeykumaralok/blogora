from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from pydantic import BaseModel


# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True, index=True)
#     full_name = Column(String, nullable=False)
#     username = Column(String, unique=True, index=True, nullable=False)
#     email = Column(String, unique=True, index=True, nullable=False)
#     hashed_password = Column(String, nullable=False)
#     is_active = Column(Boolean, default=True)
#     created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 1. MAKE SURE THIS EXACT LINE IS INSIDE YOUR USER CLASS:
    blogs = relationship("BlogPost", back_populates="owner", cascade="all, delete-orphan")


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

class BlogPost(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String, default="General")
    read_time = Column(String, default="3 min read")
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # 2. AND THIS EXACT LINE MATCHES IT INSIDE YOUR BLOGPOST CLASS:
    owner = relationship("User", back_populates="blogs")