from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    is_alumni: bool = False

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    bio: Optional[str] = None
    profile_pic: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserWithStats(User):
    followers_count: int
    following_count: int
    posts_count: int

# Post Schemas
class PostCreate(BaseModel):
    content: str
    media_url: Optional[str] = None

class Post(BaseModel):
    id: int
    content: str
    media_url: Optional[str] = None
    author_id: int
    created_at: datetime
    author: User
    likes_count: int
    comments_count: int
    
    class Config:
        from_attributes = True

# Comment Schemas
class CommentCreate(BaseModel):
    content: str

class Comment(BaseModel):
    id: int
    content: str
    post_id: int
    author_id: int
    created_at: datetime
    author: User
    
    class Config:
        from_attributes = True

# Event Schemas
class EventCreate(BaseModel):
    title: str
    description: str
    event_date: datetime
    location: str

class Event(BaseModel):
    id: int
    title: str
    description: str
    event_date: datetime
    location: str
    creator_id: int
    created_at: datetime
    creator: User
    
    class Config:
        from_attributes = True

# Chat Schemas
class ChatMessageCreate(BaseModel):
    receiver_id: int
    message: str

class ChatMessage(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    message: str
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Token Schema
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None