import typing
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
import time
from typing import Iterator, Dict, List, Optional, Union, AsyncGenerator
from dataclasses import dataclass
import asyncio

@dataclass
class LogEvent:
    timestamp: datetime
    message: str
    log_stream: str
    ingestion_time: datetime
    level: str = 'INFO'  # Default level

class CloudWatchLogsReader:
    """A class to read and process AWS CloudWatch logs."""
    
    def __init__(self, region_name: str = None, aws_access_key: str = None, aws_secret_key: str = None):
        """Initialize the CloudWatch Logs reader."""
        session = boto3.Session(
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region_name)
        self.client = session.client('logs')
        
    def _parse_log_level(self, message: str) -> str:
        """Parse log level from message. Default to INFO if not found."""
        message_lower = message.lower()
        if 'error' in message_lower:
            return 'ERROR'
        elif 'warn' in message_lower:
            return 'WARN'
        elif 'debug' in message_lower:
            return 'DEBUG'
        return 'INFO'
        
    def get_log_events(
        self,
        log_group_name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        log_stream_name: Optional[str] = None,
        filter_pattern: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Iterator[LogEvent]:
        """Retrieve log events from CloudWatch."""
        params = {
            'logGroupName': log_group_name
        }
        
        if start_time:
            params['startTime'] = int(start_time.timestamp() * 1000)
        if end_time:
            params['endTime'] = int(end_time.timestamp() * 1000)
        if log_stream_name:
            params['logStreamNames'] = [log_stream_name]
        if filter_pattern:
            params['filterPattern'] = filter_pattern
        if limit:
            params['limit'] = limit
            
        try:
            paginator = self.client.get_paginator('filter_log_events')
            for page in paginator.paginate(**params):
                for event in page.get('events', []):
                    yield LogEvent(
                        timestamp=datetime.fromtimestamp(event['timestamp'] / 1000),
                        message=event['message'],
                        log_stream=event['logStreamName'],
                        ingestion_time=datetime.fromtimestamp(event['ingestionTime'] / 1000),
                        level=self._parse_log_level(event['message'])
                    )
                    
        except ClientError as e:
            raise Exception(f"Failed to retrieve logs: {str(e)}")
        
    def get_log_groups(self) -> List[Dict[str, str]]:
        """Retrieve available log groups."""
        try:
            paginator = self.client.get_paginator('describe_log_groups')
            log_groups = []
            for page in paginator.paginate():
                for group in page.get('logGroups', []):
                    log_groups.append({
                        'name': group['logGroupName'],
                        'arn': group.get('arn', ''),
                        'storedBytes': group.get('storedBytes', 0),
                        'creationTime': datetime.fromtimestamp(group['creationTime'] / 1000).isoformat()
                    })
            return log_groups
        except ClientError as e:
            raise Exception(f"Failed to fetch log groups: {str(e)}")


    async def tail_logs(
        self,
        log_group_name: str,
        interval: int = 5,
        filter_pattern: Optional[str] = None
    ) -> AsyncGenerator[LogEvent, None]:
        """Continuously tail logs from CloudWatch (similar to 'tail -f')."""
        last_timestamp = datetime.now() - timedelta(weeks=52)
        
        while True:
            events = list(self.get_log_events(
                log_group_name=log_group_name,
                start_time=last_timestamp,
                filter_pattern=filter_pattern
            ))
            new_events = [event for event in events if event.timestamp > last_timestamp]
            if new_events:
                for event in new_events:
                    yield event
                last_timestamp = max(event.timestamp for event in new_events)
            
            await asyncio.sleep(interval)
        