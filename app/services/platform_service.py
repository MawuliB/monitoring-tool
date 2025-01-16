from sqlalchemy.orm import Session
from ..models.credentials import Credential
from ..platforms.aws import AWSPlatform
from ..platforms.local import LocalPlatform
from typing import Dict, List, Any
import os
import platform

class PlatformService:
    @staticmethod
    def get_system_logs():
        system = platform.system().lower()
        logs = {}

        if system == "linux":
            log_dir = "/var/log"
            for file in os.listdir(log_dir):
                if file.endswith(".log"):
                    log_name = file.split(".")[0]
                    logs[log_name] = os.path.join(log_dir, file)
            logs["syslog"] = "/var/log/syslog"

        elif system == "windows":
            log_dir = r"C:\Windows\System32\winevt\Logs"
            for file in os.listdir(log_dir):
                if file.endswith(".evtx"):
                    log_name = file.split(".")[0].lower()
                    logs[log_name] = os.path.join(log_dir, file)

        return logs

    AVAILABLE_LOG_TYPES = {
        "local": get_system_logs()
    }

    @staticmethod
    def get_log_levels() -> List[str]:
        return ["debug", "info", "warn", "error"]

    @staticmethod
    async def get_user_platform(platform: str):
        """Get the platform instance for a user based on their stored credentials."""
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
