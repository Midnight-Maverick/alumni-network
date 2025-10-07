from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from database import base

followers = Table(
    'followers',
    base.metadata,
    Column('follower_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('following_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow)
)

class User(base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    fullname = Column(String)
    hashedpwd = Column(String)
    isalumni = Column(Boolean, default=False)
    bio = Column(Text, nullable=True)
    profilepic = Column(String, nullable=True)
    createdat = Column(DateTime, default=datetime.utcnow)
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")
    eventscreated = relationship("Event", back_populates="creator", cascade="all, delete-orphan")
    following = relationship(
        "User",
        secondary=followers,
        primaryjoin=id == followers.c.follower_id,
        secondaryjoin=id == followers.c.following_id,
        backref="followers"
    )
class Post(base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    mediaurl = Column(String, nullable=True)
    authorid = Column(Integer, ForeignKey("users.id"))
    createdat = Column(DateTime, default=datetime.utcnow)

    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")

class Comment(base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    postid = Column(Integer, ForeignKey("posts.id"))
    authorid = Column(Integer, ForeignKey("users.id"))
    createdat = Column(DateTime, default=datetime.utcnow)
    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")

class Like(base):
    __tablename__ = "likes"
    
    id = Column(Integer, primary_key=True, index=True)
    postid = Column(Integer, ForeignKey("posts.id"))
    userid = Column(Integer, ForeignKey("users.id"))
    createdat = Column(DateTime, default=datetime.utcnow)
    post = relationship("Post", back_populates="likes")
    user = relationship("User", back_populates="likes")
class Event(base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    eventdate = Column(DateTime)
    location = Column(String)
    creatorid = Column(Integer, ForeignKey("users.id"))
    createdat = Column(DateTime, default=datetime.utcnow)

    creator = relationship("User", back_populates="events_created")

class ChatMessage(base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    senderid = Column(Integer, ForeignKey("users.id"))
    receiverid = Column(Integer, ForeignKey("users.id"))
    message = Column(Text)
    isread = Column(Boolean, default=False)
    createdat = Column(DateTime, default=datetime.utcnow)