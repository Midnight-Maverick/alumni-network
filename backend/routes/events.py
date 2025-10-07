from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models, schemas
from auth import currentuser
router = APIRouter(prefix="/events", tags=["events"])

@router.post("/", response_model=schemas.Event)
def createevent(event: schemas.EventCreate, current_user: models.User = Depends(currentuser), db: Session = Depends(get_db)):
    dbevent = models.Event(**event.dict(), creator_id=current_user.id)
    db.add(dbevent)
    db.commit()
    db.refresh(dbevent)
    return dbevent

@router.get("/", response_model=List[schemas.Event])
def getevents(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    events = db.query(models.Event).order_by(models.Event.eventdate).offset(skip).limit(limit).all()
    return events

@router.get("/{event_id}", response_model=schemas.Event)
def getevent(event_id: int, db: Session = Depends(get_db)):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.delete("/{event_id}")
def deleteevent(event_id: int, current_user: models.User = Depends(currentuser), db: Session = Depends(get_db)):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this event")
    db.delete(event)
    db.commit()
    return {"message": "Event deleted successfully"}