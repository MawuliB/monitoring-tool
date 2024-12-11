from .base import LogPlatform
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class LocalPlatform(LogPlatform):
    async def get_logs(
        self,
        credentials: Dict[str, str],
        start_time: datetime,
        end_time: datetime,
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Read logs from local files."""
        logs = []
        path = credentials.get('path', '/var/log')  # Default path if not specified
        
        try:
            log_path = Path(path)
            if log_path.is_file():
                with open(log_path, 'r') as f:
                    for line in f:
                        logs.append({
                            'timestamp': datetime.now().isoformat(),
                            'message': line.strip(),
                            'source': 'local'
                        })
        except Exception as e:
            print(f"Error reading local logs: {e}")
        
        return logs

    def validate_credentials(self, credentials: Dict[str, str]) -> bool:
        """Local files don't require credentials."""
        return True 