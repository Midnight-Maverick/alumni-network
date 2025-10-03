from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models, schemas
from auth import get_current_user, get_password_hash

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=schemas.UserWithStats)
def get_current_user_profile(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return {
        **current_user.__dict__,
        "followers_count": len(current_user.followers),
        "following_count": len(current_user.following),
        "posts_count": len(current_user.posts)
    }

@router.get("/{user_id}", response_model=schemas.UserWithStats)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        **user.__dict__,
        "followers_count": len(user.followers),
        "following_count": len(user.following),
        "posts_count": len(user.posts)
    }

@router.get("/", response_model=List[schemas.User])
def get_users(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@router.post("/follow/{user_id}")
def follow_user(user_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_to_follow = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_to_follow:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_to_follow in current_user.following:
        raise HTTPException(status_code=400, detail="Already following this user")
    
    current_user.following.append(user_to_follow)
    db.commit()
    return {"message": "Successfully followed user"}

@router.post("/unfollow/{user_id}")
def unfollow_user(user_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_to_unfollow = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_to_unfollow:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_to_unfollow not in current_user.following:
        raise HTTPException(status_code=400, detail="Not following this user")
    
    current_user.following.remove(user_to_unfollow)
    db.commit()
    return {"message": "Successfully unfollowed user"}

@router.get("/{user_id}/followers", response_model=List[schemas.User])
def get_followers(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.followers

@router.get("/{user_id}/following", response_model=List[schemas.User])
def get_following(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.following