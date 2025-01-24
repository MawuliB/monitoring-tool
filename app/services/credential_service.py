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
        db_credential.set_credentials(credential.model_dump(exclude_none=True))
    else:
        # Create new credentials
        db_credential = Credential(
            user_id=user_id,
            platform=platform
        )
        db_credential.set_credentials(credential.model_dump(exclude_none=True))
        db.add(db_credential)
    
    db.commit()
    db.refresh(db_credential)
    
    return CredentialResponse(
        id=db_credential.id,
        platform=db_credential.platform
    ) 


async def get_credentials(db: Session, platform: str, user_id: int) -> Dict[str, Any]:
    """Get credentials for a specific platform"""
    db_credential = db.query(Credential).filter(
        Credential.user_id == user_id,
        Credential.platform == platform
    ).first()
    
    if not db_credential:
        return {}
    
    return db_credential.get_credentials()