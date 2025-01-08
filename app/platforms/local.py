from .base import LogPlatform
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import re

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
        start_time = datetime.fromisoformat(start_time.isoformat()).strftime("%Y-%m-%d %H:%M:%S")
        end_time = datetime.fromisoformat(end_time.isoformat()).strftime("%Y-%m-%d %H:%M:%S")
        
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
        
        def extract_timestamp(line: str) -> str:
            """Extract timestamp from a log line. Default to current time if not found."""
            timestamp_match = re.search(r'(\w{3})\s+(\d{1,2})\s+(\d{2}:\d{2}:\d{2})', line)
            if timestamp_match:
                month_map = {
                    'Jan': '01',
                    'Feb': '02',
                    'Mar': '03',
                    'Apr': '04',
                    'May': '05',
                    'Jun': '06',
                    'Jul': '07',
                    'Aug': '08',
                    'Sep': '09',
                    'Oct': '10',
                    'Nov': '11',
                    'Dec': '12'
                }
                month, day, time = timestamp_match.groups()
                # Ensure the day is zero-padded for consistency
                day = day.zfill(2)
                return f"{datetime.now().year}-{month_map[month]}-{day} {time}"
            
            # If no timestamp is found, return "N/A"
            return "N/A"
        
        try:
            log_path = Path(path)
            if log_path.is_file():
                with open(log_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        log_entry = {
                            'timestamp': extract_timestamp(line),
                            'message': line,
                            'source': 'local',
                            'level': parse_log_level(line)
                        }
                        # Filter by time range
                        log_time = datetime.fromisoformat(log_entry['timestamp']).strftime("%Y-%m-%d %H:%M:%S")

                        if start_time <= log_time <= end_time:
                            # Filter by name if provided
                            if 'keyword' in filters and filters['keyword'] not in line:
                                continue
                            # Filter by log level if provided
                            if 'level' in filters and log_entry['level'].upper() != filters['level']:
                                continue
                            logs.append(log_entry)
        except Exception as e:
            print(f"Error reading local logs: {e}")
        return logs

    def validate_credentials(self, credentials: Dict[str, str]) -> bool:
        """Local files don't require credentials."""
        return True