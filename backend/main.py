from ast import Dict
import os
import json
from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import redis
from database import engine, get_db, base
import models, schemas
from auth import authuser, accesstoken, getpwd, currentuser, expire
from routes import users, posts, events, chat
load_dotenv()
base.metadata.create_all(bind=engine)
app = FastAPI(title="Alumni-Student Network")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
try:
    redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
    redis_client.ping()
    print("Redis connection established")
except Exception as e:
    print(f"Redis not connected: {e}")
    redis_client = None
class connectionman:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}  

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(f"User {user_id} connected via WebSocket")

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            print(f"User {user_id} disconnected")

    async def send_personal_message(self, message: dict, user_id: int):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)

man = connectionman()


app.include_router(users.router)
app.include_router(posts.router)
app.include_router(events.router)
app.include_router(chat.router)

@app.get("/")
def read_root():
    return {"message": "Alumni-Student Network API", "status": "running"}

@app.post("/register", response_model=schemas.User)
def reg(user: schemas.UserCreate, db: Session = Depends(get_db)):
  
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    hashedpwd = getpwd(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        is_alumni=user.is_alumni,
        hashed_password=hashedpwd
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
@app.post("/token", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    userdata = authuser(db, form_data.username, form_data.password)
    if not userdata:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=expire)
    access_token = accesstoken(
        data={"sub": userdata.username}, expiredelta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    try:
        from jose import jwt, JWTError
        from auth import secretkey, algo
        try:
            payload = jwt.decode(token, secretkey, algorithms=[algo])
            username: str = payload.get("sub")
            if username is None:
                await websocket.close(code=1008)
                return
        except JWTError:
            await websocket.close(code=1008)
            return
        
        user = db.query(models.User).filter(models.User.username == username).first()
        if not user:
            await websocket.close(code=1008)
            return
        await man.connect(user.id, websocket)
        try:
            while True:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                chatmes = models.ChatMessage(
                    sender_id=user.id,
                    receiver_id=message_data["receiver_id"],
                    message=message_data["message"]
                )
                db.add(chatmes)
                db.commit()
                db.refresh(chatmes)
                if redis_client:
                    try:
                        chat_key = f"chat:{min(user.id, message_data['receiver_id'])}:{max(user.id, message_data['receiver_id'])}"
                        redis_client.lpush(chat_key, json.dumps({
                            "id": chatmes.id,
                            "sender_id": user.id,
                            "receiver_id": message_data["receiver_id"],
                            "message": message_data["message"],
                            "created_at": chatmes.created_at.isoformat()
                        }))
                        redis_client.ltrim(chat_key, 0, 99)
                    except Exception as e:
                        print(f"Redis error: {e}")
                resdata = {
                    "id": chatmes.id,
                    "sender_id": user.id,
                    "receiver_id": message_data["receiver_id"],
                    "message": message_data["message"],
                    "created_at": chatmes.created_at.isoformat(),
                    "sender_username": user.username,
                    "sender_full_name": user.fullname
                }
                await man.send_personal_message(resdata, message_data["receiver_id"])
                await man.send_personal_message(resdata, user.id)
                
        except WebSocketDisconnect:
            man.disconnect(user.id)
        except Exception as e:
            print(f"WebSocket error: {e}")
            man.disconnect(user.id)
    except Exception as e:
        print(f"WebSocket connection error: {e}")
        await websocket.close(code=1011)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)