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
    
    def __init__(self, region_name: str = None, profile_name: str = None):
        """
        Initialize the CloudWatch Logs reader.
        
        Args:
            region_name: AWS region name (optional)
            profile_name: AWS profile name (optional)
        """
        session = boto3.Session(profile_name=profile_name, region_name=region_name)
        self.client = session.client('logs')
        
    def list_log_groups(self, prefix: str = None) -> List[Dict]:
        """
        List available CloudWatch log groups.
        
        Args:
            prefix: Filter log groups by prefix
            
        Returns:
            List of log group details
        """
        paginator = self.client.get_paginator('describe_log_groups')
        params = {} if prefix is None else {'logGroupNamePrefix': prefix}
        
        log_groups = []
        for page in paginator.paginate(**params):
            log_groups.extend(page['logGroups'])
        return log_groups
    
    def list_log_streams(self, log_group_name: str, prefix: str = None) -> List[Dict]:
        """
        List log streams for a specific log group.
        
        Args:
            log_group_name: Name of the log group
            prefix: Filter streams by prefix
            
        Returns:
            List of log stream details
        """
        paginator = self.client.get_paginator('describe_log_streams')
        params = {
            'logGroupName': log_group_name,
            'orderBy': 'LastEventTime',
            'descending': True
        }
        if prefix:
            params['logStreamNamePrefix'] = prefix
            
        log_streams = []
        for page in paginator.paginate(**params):
            log_streams.extend(page['logStreams'])
        return log_streams
    
    def get_log_events(
        self,
        log_group_name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        log_stream_name: Optional[str] = None,
        filter_pattern: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Iterator[LogEvent]:
        """
        Retrieve log events from CloudWatch.
        
        Args:
            log_group_name: Name of the log group
            start_time: Start time for log retrieval
            end_time: End time for log retrieval
            log_stream_name: Specific log stream to query
            filter_pattern: CloudWatch Logs filter pattern
            limit: Maximum number of events to retrieve
            
        Returns:
            Iterator of LogEvent objects
        """
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
            event_count = 0
            
            for page in paginator.paginate(**params):
                for event in page.get('events', []):
                    if limit and event_count >= limit:
                        return
                        
                    yield LogEvent(
                        timestamp=datetime.fromtimestamp(event['timestamp'] / 1000),
                        message=event['message'],
                        log_stream=event['logStreamName'],
                        ingestion_time=datetime.fromtimestamp(event['ingestionTime'] / 1000)
                    )
                    event_count += 1
                    
        except ClientError as e:
            raise Exception(f"Failed to retrieve logs: {str(e)}")
    
    def tail_logs(
        self,
        log_group_name: str,
        interval: int = 5,
        filter_pattern: Optional[str] = None
    ) -> Iterator[LogEvent]:
        """
        Continuously tail logs from CloudWatch (similar to 'tail -f').
        
        Args:
            log_group_name: Name of the log group
            interval: Polling interval in seconds
            filter_pattern: CloudWatch Logs filter pattern
            
        Returns:
            Iterator of LogEvent objects
        """
        last_timestamp = datetime.now() - timedelta(minutes=1)
        
        while True:
            events = list(self.get_log_events(
                log_group_name=log_group_name,
                start_time=last_timestamp,
                filter_pattern=filter_pattern
            ))
            
            if events:
                for event in events:
                    yield event
                last_timestamp = max(event.timestamp for event in events)
                
            time.sleep(interval)