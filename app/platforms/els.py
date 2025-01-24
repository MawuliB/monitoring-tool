from .base import LogPlatform
from ..reader.cloud import ElasticsearchLogsReader
from typing import Optional

class ElasticsearchPlatform(LogPlatform):
    async def get_logs(self, credentials, start_time, end_time, filters):
        if not filters.get('log_group'):
            raise ValueError("index is required")
        
        reader = ElasticsearchLogsReader(
            host=credentials['host'],
            username=credentials.get('username'),
            password=credentials.get('password'),
            api_key=credentials.get('api_key')
        )
        
        logs = reader.get_log_events(
            index_name=filters['log_group'],
            start_time=start_time,
            end_time=end_time,
            query_filter=filters.get('level')
        )
        
        return [
            {
                'timestamp': log.timestamp.isoformat(),
                'message': log.message,
                'source': 'elasticsearch',
                'level': log.level
            } for log in logs
        ]

    async def get_log_groups(self, credentials):
        reader = ElasticsearchLogsReader(
            host=credentials['host'],
            username=credentials.get('username'),
            password=credentials.get('password'),
            api_key=credentials.get('api_key')
        )
        return reader.get_indices()

    def validate_credentials(self, credentials):
        required = {'host'}
        optional = {'username', 'password', 'api_key'}
        
        # Must have host, and at least one authentication method
        return (
            'host' in credentials and 
            (('username' in credentials and 'password' in credentials) or 'api_key' in credentials)
        )

    async def tail_logs(
        self, 
        credentials, 
        index_name: str, 
        interval: int = 5, 
        filter_pattern: Optional[str] = None
        ):
        """Asynchronously tail logs from Elasticsearch."""
        reader = ElasticsearchLogsReader(
            host=credentials['host'],
            username=credentials.get('username'),
            password=credentials.get('password'),
            api_key=credentials.get('api_key')
        )
        try:
            async for log_event in reader.tail_logs(index_name, interval, filter_pattern):
                yield log_event
        except Exception as e:
            print(f"Error while tailing logs: {str(e)}")