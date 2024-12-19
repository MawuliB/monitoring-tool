from typing import Dict, Any
from sqlalchemy.orm import Session
from ..models import Credential
from ..schemas import CredentialCreate, CredentialResponse

async def create_credential(
    db: Session,
    platform: str,
    credential: CredentialCreate,
    user_id: int
) -> CredentialResponse:
    """Create or update credentials for a user's platform"""
    # Check for existing credentials
    db_credential = db.query(Credential).filter(
        Credential.user_id == user_id,
        Credential.platform == platform
    ).first()
    
    if db_credential:
        # Update existing credentials
        db_credential.set_credentials(credential.model_dump())
    else:
        # Create new credentials
        db_credential = Credential(
            user_id=user_id,
            platform=platform
        )
        db_credential.set_credentials(credential.model_dump())
        db.add(db_credential)
    
    db.commit()
    db.refresh(db_credential)
    
    return CredentialResponse(
        id=db_credential.id,
        platform=db_credential.platform
    ) 