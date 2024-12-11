import json
import os
from datetime import datetime
from pathlib import Path
from typing import Iterator, Union, Dict, List, Optional
import gzip
import re

class LogReader:
    """A class to read and parse different types of log files."""
    
    def __init__(self, log_path: Union[str, Path]):
        """
        Initialize the LogReader with a path to a log file.
        
        Args:
            log_path: Path to the log file (string or Path object)
        """
        self.log_path = Path(log_path)
        if not self.log_path.exists():
            raise FileNotFoundError(f"Log file not found: {log_path}")
            
    def _open_file(self) -> Iterator[str]:
        """Open the file, handling both plain and gzipped files."""
        if str(self.log_path).endswith('.gz'):
            return gzip.open(self.log_path, 'rt')
        return open(self.log_path, 'r')
    
    def read_plain_text(self, pattern: Optional[str] = None) -> Iterator[Dict]:
        """
        Read a plain text log file line by line.
        
        Args:
            pattern: Optional regex pattern to parse log lines
                    Default pattern matches common log formats
        
        Returns:
            Iterator of dictionaries containing parsed log entries
        """
        if pattern is None:
            # Default pattern matches: timestamp [level] message
            pattern = r'(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}(?:\.\d+)?)\s+' \
                     r'\[(?P<level>\w+)\]\s+(?P<message>.*)'
        
        regex = re.compile(pattern)
        
        with self._open_file() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                match = regex.match(line)
                if match:
                    yield match.groupdict()
                else:
                    yield {
                        'timestamp': datetime.now().isoformat(),
                        'level': 'INFO',
                        'message': line
                    }
    
    def read_json(self) -> Iterator[Dict]:
        """
        Read a JSON log file where each line is a JSON object.
        
        Returns:
            Iterator of dictionaries containing parsed JSON log entries
        """
        with self._open_file() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as e:
                    yield {'error': f'Failed to parse JSON: {e}', 'raw': line}
    
    @staticmethod
    def find_logs(directory: Union[str, Path], pattern: str = "*.log") -> List[Path]:
        """
        Find all log files in a directory matching a pattern.
        
        Args:
            directory: Directory to search for log files
            pattern: Glob pattern to match log files (default: "*.log")
            
        Returns:
            List of Path objects for matching log files
        """
        directory = Path(directory)
        return list(directory.glob(pattern))

def get_system_logs() -> List[Path]:
    """
    Get paths to common system log locations based on the operating system.
    
    Returns:
        List of Path objects for system log directories
    """
    if os.name == 'posix':  # Linux/Unix
        log_paths = [
            Path('/var/log'),
            Path.home() / '.local' / 'log'
        ]
    else:  # Windows
        log_paths = [
            Path(os.getenv('LOCALAPPDATA', '')) / 'Logs',
            Path(os.getenv('PROGRAMDATA', '')) / 'Logs'
        ]
    
    return [p for p in log_paths if p.exists()]