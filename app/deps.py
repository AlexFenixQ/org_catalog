from .database import SessionLocal
from fastapi import Header, HTTPException

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

API_KEY = "SECRET_KEY_123"

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
