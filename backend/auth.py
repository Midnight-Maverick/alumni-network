import os
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
import bcrypt
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
load_dotenv()
secretkey = os.getenv("SECRET_KEY")
algo = os.getenv("ALGORITHM")
expire = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 10080))

oauth2 = OAuth2PasswordBearer(tokenUrl="token")

def verifypwd(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def getpwd(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def accesstoken(data: dict, expiredelta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expiredelta:
        expire = datetime.utcnow() + expiredelta
    else:
        expire = datetime.utcnow() + timedelta(minutes=expire)
    to_encode.update({"exp": expire})
    encode = jwt.encode(to_encode, secretkey, algorithm=algo)
    return encode

def currentuser(token: str = Depends(oauth2), db: Session = Depends(get_db)):
    cred = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, secretkey, algorithms=[algo])
        username: str = payload.get("sub")
        if username is None:
            raise cred
    except JWTError:
        raise cred
    
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise cred
    return user

def authuser(db: Session, username: str, password: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        return False
    if not verifypwd(password, user.hashedpwd):
        return False
    return user