from typing import Union

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

app = FastAPI()

# Database setup
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String, nullable=False)
    receiver = Column(String, nullable=False)
    content = Column(String, nullable=False)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UserCreate(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class MessageCreate(BaseModel):
    sender: str
    receiver: str
    content: str


class MessageUpdate(BaseModel):
    content: Union[str, None] = None


@app.post("/api/users")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    new_user = User(username=user.username, password=user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}


@app.get("/api/users")
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


@app.post("/api/users/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = (
        db.query(User)
        .filter(User.username == user.username, User.password == user.password)
        .first()
    )
    if db_user:
        return {"message": "Login successful"}
    raise HTTPException(status_code=400, detail="Invalid credentials")


@app.post("/api/messages")
def send_message(message: MessageCreate, db: Session = Depends(get_db)):
    if not db.query(User).filter(User.username == message.sender).first():
        raise HTTPException(status_code=400, detail="Sender does not exist")
    if not db.query(User).filter(User.username == message.receiver).first():
        raise HTTPException(status_code=400, detail="Receiver does not exist")
    new_message = Message(
        sender=message.sender, receiver=message.receiver, content=message.content
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return {"message": "Message sent successfully", "message_id": new_message.id}


@app.get("/api/messages")
def list_messages(receiver: str, db: Session = Depends(get_db)):
    user_messages = db.query(Message).filter(Message.receiver == receiver).all()
    return user_messages


@app.delete("/api/messages/{message_id}")
def delete_message(message_id: int, db: Session = Depends(get_db)):
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    db.delete(message)
    db.commit()
    return {"message": "Message deleted successfully"}


@app.patch("/api/messages/{message_id}")
def update_message(
    message_id: int, message_update: MessageUpdate, db: Session = Depends(get_db)
):
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    if message_update.content is not None:
        message.content = message_update.content
    db.commit()
    db.refresh(message)
    return {"message": "Message updated successfully"}


@app.get("/health")
def read_root():
    return {"status": "ok"}
