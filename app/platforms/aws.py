from .base import LogPlatform
from ..cloud import CloudWatchLogsReader

class AWSPlatform(LogPlatform):
    async def get_logs(self, credentials, start_time, end_time, filters):
        if not filters.get('log_group'):
            raise ValueError("log_group is required")
            
        reader = CloudWatchLogsReader(
            region_name=credentials['region'],
            aws_access_key=credentials['access_key'],
            aws_secret_key=credentials['secret_key']
        )
        
        logs = reader.get_log_events(
            log_group_name=filters['log_group'],
            start_time=start_time,
            end_time=end_time,
            filter_pattern=filters.get('pattern')
        )
        
        return [
            {
                'timestamp': log.timestamp.isoformat(),
                'message': log.message,
                'source': log.log_stream,
                'level': log.level
            } for log in logs
        ]

    async def get_log_groups(self, credentials):
        print(credentials)
        reader = CloudWatchLogsReader(
            region_name=credentials['region'],
            aws_access_key=credentials['access_key'],
            aws_secret_key=credentials['secret_key']
        )
        return reader.get_log_groups()

    def validate_credentials(self, credentials):
        required = {'access_key', 'secret_key', 'region'}
        return all(key in credentials for key in required)