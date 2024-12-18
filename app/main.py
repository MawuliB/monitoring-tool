from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
from datetime import datetime, timedelta

from .database import get_db, engine
from .models import credentials, logs, users
from .schemas import CredentialCreate, CredentialResponse, LogQuery, UserCreate, User, Token
from .services import log_service, credential_service
from .auth import (
    get_current_user,
    authenticate_user,
    create_access_token,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Create tables
users.Base.metadata.create_all(bind=engine)
credentials.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Log Management System")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/register", response_model=User)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    db_user = db.query(users.User).filter(users.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_user = users.User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Get access token"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/credentials/{platform}", response_model=CredentialResponse)
async def add_credentials(
    platform: str,
    credential: CredentialCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add credentials for a specific platform"""
    return await credential_service.create_credential(db, platform, credential, current_user.id)

@app.get("/logs", response_model=List[dict])
async def get_logs(
    platform: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve logs based on query parameters"""
    query = LogQuery(platform=platform, start_time=start_time, end_time=end_time)
    return await log_service.get_logs(db, query, current_user.id)

@app.get("/log-groups")
async def get_log_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get available log groups for the user's platform."""
    platform = await platform_service.get_user_platform(db, current_user.id)
    if not platform:
        raise HTTPException(status_code=404, detail="No platform configured")
    
    try:
        log_groups = await platform.get_log_groups(platform.credentials)
        return {"log_groups": log_groups}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/platforms")
async def get_platforms():
    """Get list of supported platforms"""
    return {
        "platforms": [
            {
                "id": "aws",
                "name": "AWS CloudWatch",
                "required_fields": ["access_key", "secret_key", "region"]
            },
            {
                "id": "local",
                "name": "Local Files",
                "required_fields": ["path"]
            }
        ]
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", reload=True) 