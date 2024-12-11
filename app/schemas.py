from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class CredentialCreate(BaseModel):
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    region: Optional[str] = None
    path: Optional[str] = None

class CredentialResponse(BaseModel):
    id: int
    platform: str

class LogQuery(BaseModel):
    platform: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    filters: Dict[str, Any] = {} 