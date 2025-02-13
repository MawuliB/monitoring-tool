import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta, timezone
from typing import Iterator, Dict, List, Optional, Union, AsyncGenerator
from dataclasses import dataclass
import asyncio
from google.cloud import logging_v2
from google.cloud.logging_v2.services.logging_service_v2 import LoggingServiceV2Client
from google.cloud.logging_v2.types import ListLogsRequest
from google.oauth2 import service_account
from elasticsearch import Elasticsearch
from azure.identity import ClientSecretCredential
from azure.monitor.query import LogsQueryClient

@dataclass
class LogEvent:
    timestamp: datetime
    message: str
    log_stream: str
    ingestion_time: Optional[datetime] = None
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



class GoogleCloudLogsReader:
    """A class to read and process Google Cloud logs."""
    
    def __init__(
        self, 
        project_id: str, 
        credentials_path: Optional[str] = None,
        service_account_info: Optional[dict] = None
    ):
        """Initialize the Google Cloud logs reader."""
        if credentials_path:
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
        elif service_account_info:
            credentials = service_account.Credentials.from_service_account_info(
                service_account_info,
                scopes=['https://www.googleapis.com/auth/cloud-platform',
                        'https://www.googleapis.com/auth/logging.read'
                ]
            )
        else:
            raise ValueError("Either credentials_path or service_account_info must be provided")
        
        # Initialize logging client
        self.client = logging_v2.Client(project=project_id, credentials=credentials)
        self.project_id = project_id

        # Initialize LoggingServiceV2Client for list_logs
        self.logs_client = LoggingServiceV2Client(credentials=credentials)
    
    
    def _parse_log_level(self, severity: Union[str, None]) -> str:
        """Parse log severity to standard levels."""
        if not severity:
            return 'INFO'
        
        severity_map = {
            'EMERGENCY': 'ERROR',
            'ALERT': 'ERROR',
            'CRITICAL': 'ERROR',
            'ERROR': 'ERROR',
            'WARNING': 'WARN',
            'NOTICE': 'INFO',
            'INFO': 'INFO',
            'DEBUG': 'DEBUG'
        }
        
        return severity_map.get(severity.upper(), 'INFO')
    
    def get_log_events(
        self,
        log_name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        filter_pattern: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Iterator[LogEvent]:
        """Retrieve log events from Google Cloud Logging."""
        # # remove url encoding
        # log_name = log_name.replace('%2F', '/') # will uncomment this later
        # cut only the log name
        log_name = log_name.split('/')[-1]
        print(log_name)

        logger = self.client.logger(log_name)

        # Helper function to format timestamps
        def format_ts(ts: datetime) -> str:
            """Convert to RFC 3339 format with Z suffix."""
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)  # Now recognizes timezone
            utc_ts = ts.astimezone(timezone.utc)
            return utc_ts.isoformat(timespec="microseconds").replace("+00:00", "Z")
        
        # Construct filter
        filter_parts = []
        if start_time:
            filter_parts.append(f'timestamp >= "{format_ts(start_time)}"')
        if end_time:
            filter_parts.append(f'timestamp <= "{format_ts(end_time)}"')
        if filter_pattern:
            filter_parts.append(filter_pattern)
        

        
        # Apply filters
        log_filter = ' AND '.join(filter_parts) if filter_parts else None
        
        try:
            entries = logger.list_entries(filter_=log_filter, page_token=None, page_size=limit or 1000)
            
            for entry in entries:
                yield LogEvent(
                    timestamp=entry.timestamp,
                    message=str(entry.payload),
                    log_stream=entry.log_name,
                    level=self._parse_log_level(entry.severity)
                )
        
        except Exception as e:
            raise Exception(f"Failed to retrieve logs: {str(e)}")
    
    def get_log_names(self) -> List[Dict[str, str]]:
        """Retrieve available log names."""
        request = ListLogsRequest(
            resource_names=[f"projects/{self.project_id}"],
            page_size=500
        )
        logs = self.logs_client.list_logs(request=request)
        return [{'name': log} for log in logs]
    
    async def tail_logs(
        self,
        log_name: str,
        interval: int = 5,
        filter_pattern: Optional[str] = None
    ) -> AsyncGenerator[LogEvent, None]:
        """Continuously tail logs from Google Cloud Logging."""
        last_timestamp = datetime.now() - timedelta(weeks=52)
        
        while True:
            events = list(self.get_log_events(
                log_name=log_name,
                start_time=last_timestamp,
                filter_pattern=filter_pattern
            ))
            
            new_events = [event for event in events if event.timestamp > last_timestamp]
            
            if new_events:
                for event in new_events:
                    yield event
                last_timestamp = max(event.timestamp for event in new_events)
            
            await asyncio.sleep(interval)





class ElasticsearchLogsReader:
    """A class to read and process Elasticsearch logs."""
    
    def __init__(
        self, 
        host: str, 
        username: Optional[str] = None, 
        password: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """Initialize the Elasticsearch logs reader."""
        if api_key:
            self.client = Elasticsearch(
                hosts=[host],
                api_key=api_key
            )
        else:
            self.client = Elasticsearch(
                hosts=[host],
                basic_auth=(username, password) if username and password else None
            )
    
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
        index_name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        query_filter: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Iterator[LogEvent]:
        """Retrieve log events from Elasticsearch."""
        query = {
            "query": {
                "bool": {
                    "filter": []
                }
            },
            "sort": [{"@timestamp": {"order": "desc"}}]
        }
        
        # Time range filter
        if start_time or end_time:
            time_range = {}
            if start_time:
                time_range["gte"] = start_time
            if end_time:
                time_range["lte"] = end_time
            query["query"]["bool"]["filter"].append({"range": {"@timestamp": time_range}})
        
        # Log level filter
        if query_filter:
            query["query"]["bool"]["filter"].append({"match": {"level": query_filter}})
        
        # Set limit
        if limit:
            query["size"] = limit
        
        try:
            results = self.client.search(index=index_name, body=query)
            
            for hit in results['hits']['hits']:
                source = hit['_source']
                yield LogEvent(
                    timestamp=datetime.fromisoformat(source.get('@timestamp', datetime.now().isoformat())),
                    message=str(source.get('message', '')),
                    log_stream=str(source.get('log_stream', 'Unknown')),
                    level=source.get('level', self._parse_log_level(str(source.get('message', ''))))
                )
        
        except Exception as e:
            raise Exception(f"Failed to retrieve logs: {str(e)}")
    
    def get_indices(self) -> List[Dict[str, str]]:
        """Retrieve available indices."""
        indices = self.client.indices.get(index='*')
        return [
            {
                'name' : name,
                'health' : info.get('health', 'unknown'),
                'status' : info.get('status', 'unknown'),
            } for name, info in indices.items()
        ]
    
    async def tail_logs(
        self,
        index_name: str,
        interval: int = 5,
        filter_pattern: Optional[str] = None
    ) -> AsyncGenerator[LogEvent, None]:
        """Continuously tail logs from Elasticsearch."""
        last_timestamp = datetime.now() - timedelta(weeks=52)
        
        while True:
            events = list(self.get_log_events(
                index_name=index_name,
                start_time=last_timestamp,
                query_filter=filter_pattern
            ))
            
            new_events = [event for event in events if event.timestamp > last_timestamp]
            
            if new_events:
                for event in new_events:
                    yield event
                last_timestamp = max(event.timestamp for event in new_events)
            
            await asyncio.sleep(interval)




class AzureLogReader:
    """A class to read and process Azure Log Analytics logs."""
    
    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        """Initialize the Azure Log Analytics reader."""
        self.credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
    
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
        workspace_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        query_filter: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Iterator[LogEvent]:
        """Retrieve log events from Azure Log Analytics."""
        client = LogsQueryClient(self.credential)
        
        # Construct query
        query = "union *"
        if query_filter:
            query += f" | where Severity == '{query_filter}'"
        
        # Time range
        start_time = start_time or datetime.now() - timedelta(hours=1)
        end_time = end_time or datetime.now()
        
        # Limit
        if limit:
            query += f" | take {limit}"
        
        try:
            result = client.query_workspace(workspace_id, query, 
                                            start_time=start_time, 
                                            end_time=end_time)
            
            for row in result.tables[0].rows:
                yield LogEvent(
                    timestamp=row['TimeGenerated'],
                    message=str(row.get('Message', '')),
                    log_stream=str(row.get('Source', 'Unknown')),
                    level=self._parse_log_level(str(row.get('Message', '')))
                )
        
        except Exception as e:
            raise Exception(f"Failed to retrieve logs: {str(e)}")
    
    def get_log_workspaces(self) -> List[Dict[str, str]]:
        """Retrieve available log workspaces."""
        # Note: Implementation depends on specific Azure SDK methods
        # This is a placeholder and might need adjustment based on exact Azure SDK capabilities
        return []
    
    async def tail_logs(
        self,
        workspace_id: str,
        interval: int = 5,
        filter_pattern: Optional[str] = None
    ) -> AsyncGenerator[LogEvent, None]:
        """Continuously tail logs from Azure Log Analytics."""
        last_timestamp = datetime.now() - timedelta(weeks=52)
        
        while True:
            events = list(self.get_log_events(
                workspace_id=workspace_id,
                start_time=last_timestamp,
                query_filter=filter_pattern
            ))
            
            new_events = [event for event in events if event.timestamp > last_timestamp]
            
            if new_events:
                for event in new_events:
                    yield event
                last_timestamp = max(event.timestamp for event in new_events)
            
            await asyncio.sleep(interval)