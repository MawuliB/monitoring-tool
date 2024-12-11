from unified_logs import UnifiedLogReader
from datetime import datetime, timedelta

# Initialize the unified reader
reader = UnifiedLogReader(aws_region='us-east-1')

# Read local logs
local_logs = reader.get_local_logs(
    log_path='/var/log/syslog',
    pattern=r'(?P<timestamp>.*?) (?P<message>.*)'
)
for log in local_logs:
    print(f"Local log: {log}")

# Read cloud logs
end_time = datetime.now()
start_time = end_time - timedelta(hours=1)

cloud_logs = reader.get_cloud_logs(
    log_group='/aws/lambda/test'
)
for log in cloud_logs:
    print(f"Cloud log: {log.timestamp} - {log.message}")

# # Tail cloud logs
# for log in reader.tail_logs('cloud', log_group_name='/aws/lambda/test'):
#     print(f"New log: {log.message}")