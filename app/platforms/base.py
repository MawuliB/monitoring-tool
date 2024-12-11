from abc import ABC, abstractmethod
from typing import Dict, List, Any
from datetime import datetime

class LogPlatform(ABC):
    @abstractmethod
    async def get_logs(
        self,
        credentials: Dict[str, str],
        start_time: datetime,
        end_time: datetime,
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Retrieve logs from the platform"""
        pass

    @abstractmethod
    def validate_credentials(self, credentials: Dict[str, str]) -> bool:
        """Validate platform-specific credentials"""
        pass 