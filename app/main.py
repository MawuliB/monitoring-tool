import json
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
from datetime import datetime, timedelta
from fastapi import Query

from app.platforms.aws import AWSPlatform

from .database import get_db, engine
from .models import credentials, logs, users
from .schemas import CredentialCreate, CredentialResponse, LogQuery, UserCreate, User, Token
from .services import log_service, credential_service, platform_service
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

platform_service = platform_service.PlatformService()

local_log_dict = {
    "system": "syslog",
    "auth": "auth.log"
}

app = FastAPI(title="Log Management System")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

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

@app.get("/credentials/{platform}")
async def get_credentials(
    platform: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get credentials for a specific platform"""
    return await credential_service.get_credentials(db, platform, current_user.id)

@app.get("/log-types/{platform}")
async def get_log_types(platform: str):
    """Get available log types for a platform."""
    log_types = await platform_service.get_log_types(platform)
    return {"logTypes": log_types}

@app.get("/log-groups")
async def get_log_groups(
    platform: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get available log groups for the specified platform."""
    try:
        if platform == "aws":
            credential = db.query(credentials.Credential).filter(
                credentials.Credential.user_id == current_user.id,
                credentials.Credential.platform == platform
            ).first()
            
            if not credential:
                raise HTTPException(status_code=404, detail="Credentials not found")
            
            platform_instance = await platform_service.get_user_platform(platform)
            if not platform_instance:
                raise HTTPException(status_code=404, detail="Platform not configured")
                
            log_groups = await platform_instance.get_log_groups(credential.get_credentials())
        
        return {"log_groups": log_groups}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs")
async def get_logs(
    platform: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    log_type: Optional[str] = None,
    log_group: Optional[str] = None,
    log_level: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all logs for the specified platform and filters."""
    try:
        platform_instance = await platform_service.get_user_platform(platform)
        if not platform_instance:
            raise HTTPException(status_code=404, detail="Platform not configured")

        # Initialize filters
        filters = {}

        if log_type and platform == "local":
            filters["path"] = f"/var/log/{local_log_dict[log_type]}"

        if log_group and platform == "aws":
            filters["log_group"] = log_group

        if log_level:
            filters["level"] = log_level

        if keyword:
            filters["keyword"] = keyword

        logs = await platform_instance.get_logs(
            credentials={"path": filters.get("path", "/var/log/syslog")} if platform == "local" else db.query(credentials.Credential).filter(
                credentials.Credential.user_id == current_user.id,
                credentials.Credential.platform == platform
            ).first().get_credentials(),
            start_time=start_time or datetime.now() - timedelta(hours=1),
            end_time=end_time or datetime.now(),
            filters=filters
        )
        
        return {
            "logs": logs
        }

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs/tail/aws")
async def tail_logs(
    log_group_name: str, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
    ):
    credential = db.query(credentials.Credential).filter(
        credentials.Credential.user_id == current_user.id,
        credentials.Credential.platform == "aws"
    ).first().get_credentials()
    aws_platform = AWSPlatform()
    try:
        async def event_stream():
            async for log_event in aws_platform.tail_logs(credential, log_group_name):
                yield f"data: {json.dumps(log_event.__dict__, cls=DateTimeEncoder)}\n\n"

        return StreamingResponse(event_stream(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache", 
            "X-Accel-Buffering": "no", 
            "Connection": "keep-alive"
            }
        )
    except Exception as e:
        print("Error while tailing logs:", e)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app.main:app", reload=True)