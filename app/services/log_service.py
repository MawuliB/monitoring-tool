from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from ..models import Credential
from ..schemas import LogQuery
from ..platforms import get_platform_handler
from fastapi import HTTPException

async def get_logs(db: Session, query: LogQuery, user_id: Optional[int]) -> List[Dict[str, Any]]:
    """Retrieve logs from specified platforms"""
    if query.platform == 'local':
        platform = get_platform_handler('local')
        return await platform.get_logs(
            credentials={'path': '/var/log/syslog'},  # Default path
            start_time=query.start_time,
            end_time=query.end_time,
            filters=query.filters
        )
    
    # For other platforms, require authentication
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
        
    credentials = db.query(Credential).filter_by(user_id=user_id).all()
    
    all_logs = []
    for cred in credentials:
        platform = get_platform_handler(cred.platform)
        if platform:
            platform_creds = cred.get_credentials()
            logs = await platform.get_logs(
                credentials=platform_creds,
                start_time=query.start_time,
                end_time=query.end_time,
                filters=query.filters
            )
            all_logs.extend(logs)
    
    return all_logs 