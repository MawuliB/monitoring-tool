from .base import LogPlatform
from ..reader.cloud import AzureLogReader
from typing import Optional

class AzurePlatform(LogPlatform):
    async def get_logs(self, credentials, start_time, end_time, filters):
        if not filters.get('log_group'):
            raise ValueError("log_workspace is required")
        
        reader = AzureLogReader(
            tenant_id=credentials['tenant_id'],
            client_id=credentials['client_id'],
            client_secret=credentials['client_secret'],
            subscription_id=credentials['subscription_id']
        )
        
        logs = reader.get_log_events(
            workspace_id=filters['log_group'],
            start_time=start_time,
            end_time=end_time,
            query_filter=filters.get('level')
        )
        
        return [
            {
                'timestamp': log.timestamp.isoformat(),
                'message': log.message,
                'source': 'azure',
                'level': log.level
            } for log in logs
        ]

    async def get_log_groups(self, credentials):
        reader = AzureLogReader(
            tenant_id=credentials['tenant_id'],
            client_id=credentials['client_id'],
            client_secret=credentials['client_secret'],
            subscription_id=credentials['subscription_id']
        )
        return reader.get_log_workspaces()

    def validate_credentials(self, credentials):
        required = {'tenant_id', 'client_id', 'client_secret'}
        return all(key in credentials for key in required)

    async def tail_logs(
        self, 
        credentials, 
        log_workspace_id: str, 
        interval: int = 5, 
        filter_pattern: Optional[str] = None
        ):
        """Asynchronously tail logs from Azure Log Analytics."""
        reader = AzureLogReader(
            tenant_id=credentials['tenant_id'],
            client_id=credentials['client_id'],
            client_secret=credentials['client_secret'],
            subscription_id=credentials['subscription_id']
        )
        try:
            async for log_event in reader.tail_logs(log_workspace_id, interval, filter_pattern):
                yield log_event
        except Exception as e:
            print(f"Error while tailing logs: {str(e)}")