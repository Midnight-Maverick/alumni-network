from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models, schemas
from auth import currentuser
router = APIRouter(prefix="/chat", tags=["chat"])
@router.get("/history/{user_id}", response_model=List[schemas.ChatMessage])
def chathis(user_id: int, skip: int = 0, limit: int = 50, current_user: models.User = Depends(currentuser), db: Session = Depends(get_db)):
    messages = db.query(models.ChatMessage).filter(
        ((models.ChatMessage.senderid == current_user.id) & (models.ChatMessage.receiverid == user_id)) |
        ((models.ChatMessage.senderid == user_id) & (models.ChatMessage.receiverid == current_user.id))
    ).order_by(models.ChatMessage.createdat.desc()).offset(skip).limit(limit).all()

    return messages[::-1]  
@router.get("/conversations")
def getconversations(current_user: models.User = Depends(currentuser), db: Session = Depends(get_db)):
    # Get all users current user has chatted with
    sent = db.query(models.ChatMessage.receiverid).filter(models.ChatMessage.senderid == current_user.id).distinct()
    received = db.query(models.ChatMessage.senderid).filter(models.ChatMessage.receiverid == current_user.id).distinct()
    userids = set([r[0] for r in sent] + [r[0] for r in received])
    users = db.query(models.User).filter(models.User.id.in_(userids)).all()
    
    return users