from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
class UserBase(BaseModel):
    email: EmailStr
    username: str
    fullname: str
    isalumni: bool = False
class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    bio: Optional[str] = None
    profilepic: Optional[str] = None
    createdat: datetime

    class Config:
        from_attributes = True

class UserWithStats(User):
    followerscount: int
    followingcount: int
    postscount: int

class PostCreate(BaseModel):
    content: str
    mediaurl: Optional[str] = None

class Post(BaseModel):
    id: int
    content: str
    mediaurl: Optional[str] = None
    authorid: int
    createdat: datetime
    author: User
    likescount: int
    commentscount: int

    class Config:
        from_attributes = True

class CommentCreate(BaseModel):
    content: str

class Comment(BaseModel):
    id: int
    content: str
    postid: int
    authorid: int
    createdat: datetime
    author: User
    
    class Config:
        from_attributes = True

class EventCreate(BaseModel):
    title: str
    description: str
    eventdate: datetime
    location: str

class Event(BaseModel):
    id: int
    title: str
    description: str
    eventdate: datetime
    location: str
    creatorid: int
    createdat: datetime
    creator: User
    class Config:
        from_attributes = True
class ChatMessageCreate(BaseModel):
    receiverid: int
    message: str
class ChatMessage(BaseModel):
    id: int
    senderid: int
    receiverid: int
    message: str
    isread: bool
    createdat: datetime
    
    class Config:
        from_attributes = True
class Token(BaseModel):
    accesstoken: str
    tokentype: str
class TokenData(BaseModel):
    username: Optional[str] = None