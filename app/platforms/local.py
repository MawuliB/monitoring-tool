from .base import LogPlatform
from pathlib import Path
from datetime import datetime
from typing import AsyncGenerator, Dict, List, Any
import re
import asyncio
import os

class LocalPlatform(LogPlatform):

    def parse_log_level(self, line: str) -> str:
            """Parse log level from line. Default to INFO if not found."""
            line_lower = line.lower()
            if 'error' in line_lower:
                return 'ERROR'
            elif 'warn' in line_lower:
                return 'WARN'
            elif 'debug' in line_lower:
                return 'DEBUG'
            return 'INFO'
        

    def extract_timestamp(self, line: str) -> str:
        # Try ISO format first (cloud logs)
        iso_match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', line)
        if iso_match:
            return iso_match.group(1).replace('T', ' ')

        # Try syslog format (local logs)
        syslog_match = re.search(r'(\w{3})\s+(\d{1,2})\s+(\d{2}:\d{2}:\d{2})', line)
        if syslog_match:
            month_map = {
                'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
            }
            month, day, time = syslog_match.groups()
            day = day.zfill(2)  # Ensure day is zero-padded
            return f"{datetime.now().year}-{month_map[month]}-{day} {time}"

        # Try additional formats here
        # Example: logs with different date format
        alt_match = re.search(r'(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2}:\d{2})', line)
        if alt_match:
            date, time = alt_match.groups()
            dt = datetime.strptime(f"{date} {time}", "%m/%d/%Y %H:%M:%S")
            return dt.strftime("%Y-%m-%d %H:%M:%S")

        # If no timestamp is found, return current time
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
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
        
        try:
            log_path = Path(path)
            if log_path.is_file():
                with open(log_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        log_entry = {
                            'timestamp': self.extract_timestamp(line),
                            'message': line,
                            'source': 'local',
                            'level': self.parse_log_level(line)
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
    
    async def tail_logs(
        self, 
        credentials: Dict[str, str]
        ) -> AsyncGenerator[Dict[str, Any], None]:
        ''' Tail logs from local files '''
        path = credentials.get('path', '/var/log/syslog')  # Default path if not specified
        log_path = Path(path)
        if log_path.is_file():
            with open(log_path, 'r') as f:
                f.seek(0, os.SEEK_END)
                while True:
                    line = f.readline()
                    if not line:
                        await asyncio.sleep(1)  # Wait for 1 second before checking again
                        continue
                    log_entry = {
                        'timestamp': self.extract_timestamp(line),
                        'message': line,
                        'source': 'local',
                        'level': self.parse_log_level(line)
                    }
                    yield log_entry
                
