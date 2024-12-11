from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
from datetime import datetime

from .database import get_db
from .models import credentials, logs
from .schemas import CredentialCreate, CredentialResponse, LogQuery
from .services import log_service, credential_service
from .auth import get_current_user

app = FastAPI(title="Log Management System")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/credentials/{platform}", response_model=CredentialResponse)
async def add_credentials(
    platform: str,
    credential: CredentialCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Add credentials for a specific platform"""
    return await credential_service.create_credential(db, platform, credential, current_user.id)

@app.get("/logs", response_model=List[dict])
async def get_logs(
    platform: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user) if False else None
):
    """Retrieve logs based on query parameters"""
    user_id = current_user.id if current_user else None
    query = LogQuery(platform=platform, start_time=start_time, end_time=end_time)
    return await log_service.get_logs(db, query, user_id)

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

if __name__ == "__main__":
    uvicorn.run("app.main:app", reload=True) 