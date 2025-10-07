from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import session
from database import get_db
from auth import currentuser
import models
import schemas
router = APIRouter(prefix="/posts", tags=["posts"])
@router.post("/", response_model=schemas.Post)
def createpost(post: schemas.PostCreate, current_user: models.User = Depends(currentuser), db: session = Depends(get_db)):
    dbpost = models.Post(**post.dict(), author_id=current_user.id)
    db.add(dbpost)
    db.commit()
    db.refresh(dbpost)
    dbpost.likescount = 0
    dbpost.commentscount = 0
    return dbpost

@router.get("/", response_model=List[schemas.Post])
def getposts(skip: int = 0, limit: int = 20, db: session = Depends(get_db)):
    posts = db.query(models.Post).order_by(models.Post.createdat.desc()).offset(skip).limit(limit).all()
    for post in posts:
        post.likescount = len(post.likes)
        post.commentscount = len(post.comments)

    return posts

@router.get("/feed", response_model=List[schemas.Post])
def get_feed(skip: int = 0, limit: int = 20, current_user: models.User = Depends(currentuser), db: session = Depends(get_db)):
    followingids = [user.id for user in current_user.following]
    followingids.append(current_user.id)
    
    posts = db.query(models.Post).filter(models.Post.authorid.in_(followingids)).order_by(models.Post.createdat.desc()).offset(skip).limit(limit).all()
    
    for post in posts:
        post.likescount = len(post.likes)
        post.commentscount = len(post.comments)

    return posts

@router.get("/{post_id}", response_model=schemas.Post)
def getpost(post_id: int, db: session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post.likescount = len(post.likes)
    post.commentscount = len(post.comments)
    return post

@router.delete("/{post_id}")
def deletepost(post_id: int, current_user: models.User = Depends(currentuser), db: session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.authorid != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    
    db.delete(post)
    db.commit()
    return {"message": "Post deleted successfully"}

@router.post("/{post_id}/like")
def likepost(post_id: int, current_user: models.User = Depends(currentuser), db: session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    existinglike = db.query(models.Like).filter(
        models.Like.postid == post_id,
        models.Like.user_id == current_user.id
    ).first()
    
    if existinglike:
        raise HTTPException(status_code=400, detail="Already liked this post")
    
    like = models.Like(post_id=post_id, user_id=current_user.id)
    db.add(like)
    db.commit()
    return {"message": "Post liked successfully"}

@router.delete("/{post_id}/like")
def unlikepost(post_id: int, current_user: models.User = Depends(currentuser), db: session = Depends(get_db)):
    like = db.query(models.Like).filter(
        models.Like.postid == post_id,
        models.Like.user_id == current_user.id
    ).first()
    
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")
    
    db.delete(like)
    db.commit()
    return {"message": "Post unliked successfully"}

@router.post("/{post_id}/comments", response_model=schemas.Comment)
def createcomment(post_id: int, comment: schemas.CommentCreate, current_user: models.User = Depends(currentuser), db: session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    db_comment = models.Comment(**comment.dict(), post_id=post_id, author_id=current_user.id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.get("/{post_id}/comments", response_model=List[schemas.Comment])
def getcomments(post_id: int, db: session = Depends(get_db)):
    comments = db.query(models.Comment).filter(models.Comment.postid == post_id).order_by(models.Comment.createdat.desc()).all()
    return comments