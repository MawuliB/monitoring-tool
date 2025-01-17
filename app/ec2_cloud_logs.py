import os
import boto3
from datetime import datetime, timedelta
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

region = os.getenv('AWS_REGION')
aws_access_key = os.getenv('ACCESS_KEYS')
aws_secret_key = os.getenv('SECRET_KEYS')
log_group_name = 'CloudsLogGroup'
log_stream_name = os.getenv('LOG_STREAM_NAME')

@dataclass
class LogEvents:
    timestamp: datetime
    message: str
    log_stream: str
    ingestion_time: datetime
    level: str = 'INFO'
    
    def __str__(self):
        return f"{self.timestamp} {self.level}: {self.message} ({self.log_stream})"
    


class CloudWatchLogsReader:
    def __init__(self, region: str, aws_access_key: str, aws_secret_key: str):
        session = boto3.Session(
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )
        self.client = session.client('logs')

    def get_log_events(self, log_group_name: str, start_time: datetime, end_time: datetime):
        params = {
            'logGroupName': log_group_name,
            'startTime': int(start_time.timestamp() * 1000),
            'endTime': int(end_time.timestamp() * 1000)
        }
        
        try:
            paginator = self.client.get_paginator('filter_log_events')
            for page in paginator.paginate(**params):
                for event in page.get('events', []):
                    yield {
                        'timestamp': datetime.fromtimestamp(event['timestamp'] / 1000).isoformat(),
                        'message': event['message'],
                        'log_stream': event['logStreamName'],
                        'ingestion_time': datetime.fromtimestamp(event['ingestionTime'] / 1000).isoformat()
                    }
        except Exception as e:
            raise Exception(f"Failed to retrieve logs: {str(e)}")

# Example usage
if __name__ == "__main__":
    reader = CloudWatchLogsReader(
        region=region,
        aws_access_key=aws_access_key,
        aws_secret_key=aws_secret_key
    )
    start_time = datetime.now() - timedelta(hours=1)
    end_time = datetime.now()
    log_group = log_group_name

    logs = reader.get_log_events(log_group_name, start_time, end_time)
    for log in logs:
        print(log )