import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
import time
from typing import Iterator, Dict, List, Optional, Union
from dataclasses import dataclass

@dataclass
class LogEvent:
    timestamp: datetime
    message: str
    log_stream: str
    ingestion_time: datetime

class CloudWatchLogsReader:
    """A class to read and process AWS CloudWatch logs."""
    
    def __init__(self, region_name: str = None, aws_access_key: str = None, aws_secret_key: str = None):
        """Initialize the CloudWatch Logs reader."""
        session = boto3.Session(
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region_name
        )
        self.client = session.client('logs')
        
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
            'logGroupName': log_group_name,
            'startFromHead': True
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
                        ingestion_time=datetime.fromtimestamp(event['ingestionTime'] / 1000)
                    )
                    
        except ClientError as e:
            raise Exception(f"Failed to retrieve logs: {str(e)}") 