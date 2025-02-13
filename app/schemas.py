from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, Dict, Any

class CredentialCreate(BaseModel):
    # aws
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    region: Optional[str] = None
    # gcp
    project_id: Optional[str] = None
    credentials_path: Optional[str] = None
    service_account_info: Optional[Dict[str, Any]] = None
    # azure
    tenant_id: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    # els
    host: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None

class CredentialResponse(BaseModel):
    id: int
    platform: str

class LogQuery(BaseModel):
    platform: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    filters: Dict[str, Any] = {} 

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None