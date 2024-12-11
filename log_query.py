import click
import sqlite3
from datetime import datetime, timedelta
import json
from typing import Optional, Dict, Any, List
from tabulate import tabulate
import re
from dataclasses import dataclass
from log_storage import LogStorage
from auth import AuthManager, requires_auth
import os

@dataclass
class QueryParams:
    """Query parameters container"""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    source_type: Optional[str] = None
    level: Optional[str] = None
    keyword: Optional[str] = None
    limit: int = 1000
    group_by: Optional[str] = None
    aggregate: Optional[str] = None

class LogQuery:
    """Advanced log querying and analysis tool."""
    
    def __init__(self, db_path: str = 'logs.db'):
        self.storage = LogStorage(db_path)
        self.auth = AuthManager()
        
        # Initialize AWS session with credentials from aws_setup
        from aws_setup import session
        self.aws_session = session
    
    def parse_time(self, time_str: str) -> datetime:
        """Parse various time formats."""
        if time_str == 'today':
            return datetime.now().replace(hour=0, minute=0, second=0)
        if time_str == 'yesterday':
            return datetime.now().replace(hour=0, minute=0, second=0) - timedelta(days=1)
        
        try:
            return datetime.fromisoformat(time_str)
        except ValueError:
            try:
                return datetime.strptime(time_str, '%Y-%m-%d')
            except ValueError:
                raise ValueError(f"Invalid time format: {time_str}")

    def build_query(self, params: QueryParams) -> tuple[str, list]:
        """Build SQL query from parameters."""
        base_query = """
            SELECT 
                l.timestamp,
                l.level,
                l.message,
                s.name as source_name,
                s.type as source_type
        """
        
        if params.aggregate:
            base_query = f"""
                SELECT 
                    {params.group_by},
                    {params.aggregate}(1) as count
            """
        
        query = f"""
            {base_query}
            FROM logs l
            JOIN sources s ON l.source_id = s.id
            WHERE 1=1
        """
        query_params = []
        
        if params.start_time:
            query += " AND datetime(l.timestamp) >= datetime(?)"
            query_params.append(params.start_time.isoformat())
        
        if params.end_time:
            query += " AND datetime(l.timestamp) <= datetime(?)"
            query_params.append(params.end_time.isoformat())
        
        if params.source_type:
            query += " AND s.type = ?"
            query_params.append(params.source_type)
        
        if params.level:
            query += " AND l.level = ?"
            query_params.append(params.level)
        
        if params.keyword:
            query += " AND l.message LIKE ?"
            query_params.append(f"%{params.keyword}%")
        
        if params.group_by:
            query += f" GROUP BY {params.group_by}"
        
        if not params.aggregate:
            query += " ORDER BY datetime(l.timestamp) DESC"
        
        if params.limit:
            query += " LIMIT ?"
            query_params.append(params.limit)
        
        print(f"DEBUG - Query: {query}")  # Debug print
        print(f"DEBUG - Params: {query_params}")  # Debug print
        
        return query, query_params

@click.group()
def cli():
    """Log Query CLI tool"""
    pass

@cli.command()
@requires_auth
@click.option('--start', '-s', help='Start time (YYYY-MM-DD or "today"/"yesterday")')
@click.option('--end', '-e', help='End time (YYYY-MM-DD)')
@click.option('--source', '-src', help='Source type (local/cloudwatch)')
@click.option('--level', '-l', help='Log level')
@click.option('--keyword', '-k', help='Keyword search')
@click.option('--limit', default=100, help='Limit results')
@click.option('--format', '-f', type=click.Choice(['table', 'json']), default='table')
def search(start, end, source, level, keyword, limit, format):
    """Search logs with various filters"""
    query_tool = LogQuery()
    
    try:
        params = QueryParams(
            start_time=query_tool.parse_time(start) if start else None,
            end_time=query_tool.parse_time(end) if end else None,
            source_type=source,
            level=level,
            keyword=keyword,
            limit=limit
        )
        
        query, query_params = query_tool.build_query(params)
        
        with query_tool.storage._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, query_params)
            results = [dict(row) for row in cursor.fetchall()]
            
            if format == 'json':
                click.echo(json.dumps(results, indent=2, default=str))
            else:
                if results:
                    click.echo(tabulate(results, headers='keys', tablefmt='grid'))
                else:
                    click.echo("No results found")
                    # Debug information
                    click.echo("\nDebug Information:")
                    click.echo(f"Database path: {query_tool.storage.db_path}")
                    
                    # Check if tables exist and have data
                    cursor.execute("SELECT COUNT(*) FROM logs")
                    log_count = cursor.fetchone()[0]
                    cursor.execute("SELECT COUNT(*) FROM sources")
                    source_count = cursor.fetchone()[0]
                    
                    click.echo(f"Total logs in database: {log_count}")
                    click.echo(f"Total sources in database: {source_count}")
                
    except Exception as e:
        click.echo(f"Error executing query: {str(e)}")
        raise

@cli.command()
@requires_auth
@click.option('--field', '-f', required=True, help='Field to group by')
@click.option('--start', '-s', help='Start time')
@click.option('--end', '-e', help='End time')
@click.option('--source', '-src', help='Source type')
def aggregate(field, start, end, source):
    """Aggregate log data"""
    query_tool = LogQuery()
    
    params = QueryParams(
        start_time=query_tool.parse_time(start) if start else None,
        end_time=query_tool.parse_time(end) if end else None,
        source_type=source,
        group_by=field,
        aggregate='COUNT'
    )
    
    query, query_params = query_tool.build_query(params)
    
    with query_tool.storage._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, query_params)
        results = [dict(row) for row in cursor.fetchall()]
    
    click.echo(tabulate(results, headers='keys', tablefmt='grid'))

@cli.command()
@click.option('--username', '-u', required=True, help='Username')
@click.option('--role', '-r', default='reader', type=click.Choice(['reader', 'admin']))
def create_user(username, role):
    """Create a new user and generate their access token"""
    try:
        auth = AuthManager()
        token = auth.create_user(username, role)
        click.echo(f"User created successfully. Access token:\n{token}")
    except ValueError as e:
        raise click.ClickException(str(e))

if __name__ == '__main__':
    cli() 