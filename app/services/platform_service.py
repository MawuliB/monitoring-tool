from sqlalchemy.orm import Session
from ..models.credentials import Credential
from ..platforms.aws import AWSPlatform
from ..platforms.local import LocalPlatform
from typing import Dict, List, Any

class PlatformService:
    AVAILABLE_LOG_TYPES = {
        "local": {
            "system": "/var/log/syslog",
            "auth": "/var/log/auth.log",
            "application": "/var/log/application.log",
            "error": "/var/log/error.log"
        }
    }

    @staticmethod
    async def get_user_platform(db: Session, user_id: int, platform: str):
        """Get the platform instance for a user based on their stored credentials."""
        credentials = db.query(Credential).filter(
            Credential.user_id == user_id,
            Credential.platform == platform
        ).first()
        if not credentials:
            return LocalPlatform()  # Default to local if no credentials

        if platform == "aws":
            return AWSPlatform()
        elif platform == "local":
            return LocalPlatform()
        
        return LocalPlatform()  # Default to local for unknown platforms

    @staticmethod
    def get_available_platforms() -> List[Dict[str, Any]]:
        """Get list of available platforms with their configurations"""
        return [
            {
                "id": "local",
                "name": "Local System Logs",
                "description": "Access and analyze local system log files",
                "logTypes": list(PlatformService.AVAILABLE_LOG_TYPES["local"].keys())
            },
            {
                "id": "aws",
                "name": "AWS CloudWatch",
                "description": "Monitor AWS CloudWatch log groups",
                "requiresCredentials": True
            }
        ]

    @staticmethod
    async def get_log_types(platform: str) -> List[str]:
        """Get available log types for a platform"""
        if platform == "local":
            return list(PlatformService.AVAILABLE_LOG_TYPES["local"].keys())
        return []

def get_available_platforms() -> List[Dict[str, Any]]:
    """Get list of available platforms with their configurations"""
    return PlatformService.get_available_platforms()

# Create a singleton instance for other methods that need instance access
platform_service_instance = PlatformService()
