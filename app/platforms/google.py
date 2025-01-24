from .base import LogPlatform
from ..reader.cloud import GoogleCloudLogsReader
from typing import Optional

class GoogleCloudPlatform(LogPlatform):
    async def get_logs(self, credentials, start_time, end_time, filters):
        if not filters.get('log_group'):
            raise ValueError("log_name is required")
        
        reader = GoogleCloudLogsReader(
            project_id=credentials['project_id'],
            credentials_path=credentials.get('credentials_path'),
            service_account_info=credentials.get('service_account_info')
        )
        
        logs = reader.get_log_events(
            log_name=filters['log_group'],
            start_time=start_time,
            end_time=end_time,
            filter_pattern=filters.get('level')
        )
        
        return [
            {
                'timestamp': log.timestamp.isoformat(),
                'message': log.message,
                'source': 'google_cloud',
                'level': log.level
            } for log in logs
        ]

    async def get_log_groups(self, credentials):
        reader = GoogleCloudLogsReader(
            project_id=credentials['project_id'],
            credentials_path=credentials.get('credentials_path'),
            service_account_info=credentials.get('service_account_info')
        )
        return reader.get_log_names()

    def validate_credentials(self, credentials):
        required = {'project_id'}
        optional = {'credentials_path', 'service_account_info'}
        
        # Must have project_id and either credentials_path or service_account_info
        return (
            'project_id' in credentials and 
            ('credentials_path' in credentials or 'service_account_info' in credentials)
        )

    async def tail_logs(
        self, 
        credentials, 
        log_name: str, 
        interval: int = 5, 
        filter_pattern: Optional[str] = None
        ):
        """Asynchronously tail logs from Google Cloud Logging."""
        reader = GoogleCloudLogsReader(
            project_id=credentials['project_id'],
            credentials_path=credentials.get('credentials_path'),
            service_account_info=credentials.get('service_account_info')
        )
        try:
            async for log_event in reader.tail_logs(log_name, interval, filter_pattern):
                yield log_event
        except Exception as e:
            print(f"Error while tailing logs: {str(e)}")