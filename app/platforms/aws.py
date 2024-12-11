from .base import LogPlatform
from ..cloud import CloudWatchLogsReader

class AWSPlatform(LogPlatform):
    async def get_logs(self, credentials, start_time, end_time, filters):
        reader = CloudWatchLogsReader(
            region_name=credentials['region'],
            aws_access_key=credentials['access_key'],
            aws_secret_key=credentials['secret_key']
        )
        
        return list(reader.get_log_events(
            log_group_name=filters.get('log_group'),
            start_time=start_time,
            end_time=end_time,
            filter_pattern=filters.get('pattern')
        ))

    def validate_credentials(self, credentials):
        required = {'access_key', 'secret_key', 'region'}
        return all(key in credentials for key in required) 