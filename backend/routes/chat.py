from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models, schemas
from auth import get_current_user
router = APIRouter(prefix="/chat", tags=["chat"])
@router.get("/history/{user_id}", response_model=List[schemas.ChatMessage])
def get_chat_history(user_id: int, skip: int = 0, limit: int = 50, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    messages = db.query(models.ChatMessage).filter(
        ((models.ChatMessage.sender_id == current_user.id) & (models.ChatMessage.receiver_id == user_id)) |
        ((models.ChatMessage.sender_id == user_id) & (models.ChatMessage.receiver_id == current_user.id))
    ).order_by(models.ChatMessage.created_at.desc()).offset(skip).limit(limit).all()
    return messages[::-1] 
@router.get("/conversations")
def get_conversations(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    sent = db.query(models.ChatMessage.receiver_id).filter(models.ChatMessage.sender_id == current_user.id).distinct()
    received = db.query(models.ChatMessage.sender_id).filter(models.ChatMessage.receiver_id == current_user.id).distinct()
    user_ids = set([r[0] for r in sent] + [r[0] for r in received])
    users = db.query(models.User).filter(models.User.id.in_(user_ids)).all()
    return users