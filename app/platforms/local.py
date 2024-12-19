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
        path = credentials.get('path', '/var/log/syslog')  # Default path if not specified
        
        def parse_log_level(line: str) -> str:
            """Parse log level from line. Default to INFO if not found."""
            line_lower = line.lower()
            if 'error' in line_lower:
                return 'ERROR'
            elif 'warn' in line_lower:
                return 'WARN'
            elif 'debug' in line_lower:
                return 'DEBUG'
            return 'INFO'
        
        try:
            log_path = Path(path)
            if log_path.is_file():
                with open(log_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        logs.append({
                            'timestamp': datetime.now().isoformat(),
                            'message': line,
                            'source': 'local',
                            'level': parse_log_level(line)
                        })
        except Exception as e:
            print(f"Error reading local logs: {e}")
        
        return logs

    def validate_credentials(self, credentials: Dict[str, str]) -> bool:
        """Local files don't require credentials."""
        return True