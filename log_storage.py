import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import time
from contextlib import contextmanager

class LogStorage:
    """Stores and manages logs in SQLite database."""
    
    def __init__(self, db_path: str = 'logs.db'):
        """
        Initialize the log storage.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_db()
    
    @contextmanager
    def _get_connection(self, max_retries: int = 5, retry_delay: float = 0.5):
        """Get database connection with retry logic."""
        attempt = 0
        while attempt < max_retries:
            try:
                conn = sqlite3.connect(self.db_path, timeout=20.0)  # Increase timeout
                conn.row_factory = sqlite3.Row
                yield conn
                return
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e):
                    attempt += 1
                    if attempt == max_retries:
                        raise
                    time.sleep(retry_delay)
                else:
                    raise
            finally:
                if 'conn' in locals():
                    conn.close()
    
    def _init_db(self) -> None:
        """Initialize database schema."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Sources table for log sources (local files, cloud services)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(name, type)
                )
            ''')
            
            # Main logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id INTEGER NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    level TEXT,
                    message TEXT NOT NULL,
                    FOREIGN KEY (source_id) REFERENCES sources(id)
                )
            ''')
            
            # Metadata table for additional log properties
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS log_metadata (
                    log_id INTEGER NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    FOREIGN KEY (log_id) REFERENCES logs(id),
                    PRIMARY KEY (log_id, key)
                )
            ''')
            
            # Indexes for better query performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_level ON logs(level)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_metadata_key ON log_metadata(key)')
            
            conn.commit()
    
    def add_source(self, name: str, source_type: str) -> int:
        """Add or get a log source."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO sources (name, type)
                VALUES (?, ?)
            ''', (name, source_type))
            
            if cursor.rowcount == 0:  # Source already exists
                cursor.execute('''
                    SELECT id FROM sources
                    WHERE name = ? AND type = ?
                ''', (name, source_type))
                return cursor.fetchone()[0]
            
            conn.commit()
            return cursor.lastrowid
    
    def store_logs(self, logs: List[Dict[str, Any]]) -> None:
        """Store multiple log entries with improved error handling."""
        successful_logs = 0
        failed_logs = 0

        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            for log in logs:
                try:
                    # Begin transaction for each log
                    cursor.execute('BEGIN TRANSACTION')
                    
                    # Get or create source
                    source_id = self.add_source(
                        name=log.get('log_group', log.get('file_path', 'unknown')),
                        source_type=log['source']
                    )
                    
                    # Extract message from content if it's a dict
                    content = log['content']
                    if isinstance(content, dict):
                        message = content.get('message', str(content))
                    else:
                        message = str(content)
                    
                    # Convert timestamp to string if it's a datetime object
                    timestamp = log['timestamp']
                    if isinstance(timestamp, datetime):
                        timestamp = timestamp.isoformat()
                    
                    # Insert log entry
                    cursor.execute('''
                        INSERT INTO logs (source_id, timestamp, level, message)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        source_id,
                        timestamp,
                        log.get('level', 'INFO'),
                        message
                    ))
                    
                    log_id = cursor.lastrowid
                    
                    # Store additional metadata
                    metadata = {
                        k: str(v) for k, v in log.items()
                        if k not in ('timestamp', 'level', 'message', 'content', 'source')
                    }
                    
                    if metadata:
                        cursor.executemany('''
                            INSERT INTO log_metadata (log_id, key, value)
                            VALUES (?, ?, ?)
                        ''', [(log_id, k, v) for k, v in metadata.items()])
                    
                    # Commit transaction for this log
                    conn.commit()
                    successful_logs += 1
                    
                except Exception as e:
                    conn.rollback()  # Rollback failed transaction
                    failed_logs += 1
                    print(f"Error storing log: {e}")
                    print(f"Problematic log entry: {log}")
                    continue
        
        print(f"\nStorage Summary:")
        print(f"Successfully stored: {successful_logs} logs")
        print(f"Failed to store: {failed_logs} logs")
    
    def query_logs(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        source_type: Optional[str] = None,
        level: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Query logs with various filters."""
        query = '''
            SELECT 
                l.id,
                l.timestamp,
                l.level,
                l.message,
                s.name as source_name,
                s.type as source_type
            FROM logs l
            JOIN sources s ON l.source_id = s.id
            WHERE 1=1
        '''
        params = []
        
        if start_time:
            query += ' AND l.timestamp >= ?'
            params.append(start_time.isoformat())
        if end_time:
            query += ' AND l.timestamp <= ?'
            params.append(end_time.isoformat())
        if source_type:
            query += ' AND s.type = ?'
            params.append(source_type)
        if level:
            query += ' AND l.level = ?'
            params.append(level)
        
        query += ' ORDER BY l.timestamp DESC LIMIT ?'
        params.append(limit)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            logs = [dict(row) for row in cursor.fetchall()]
            
            # Fetch metadata for each log
            for log in logs:
                cursor.execute('''
                    SELECT key, value
                    FROM log_metadata
                    WHERE log_id = ?
                ''', (log['id'],))
                log['metadata'] = {row['key']: row['value'] for row in cursor.fetchall()}
            
            return logs 