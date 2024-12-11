from cloud import *
from datetime import datetime, timedelta

# Initialize the reader
reader = CloudWatchLogsReader(region_name='us-east-1')

# First, list available log groups
log_groups = reader.list_log_groups()
print("Available Log Groups:")
for group in log_groups:
    print(f"- {group['logGroupName']}")

# Use an existing log group from the printed list
LOG_GROUP_NAME = '/aws/lambda/test'

# Get logs from the last hour
end_time = datetime.now()
start_time = end_time - timedelta(weeks=18)

try:
    logs = reader.get_log_events(
        log_group_name=LOG_GROUP_NAME,
        start_time=start_time,
        end_time=end_time,
        filter_pattern='REPORT'
    )

    for log in logs:
        print(f"{log.timestamp}: {log.message}")
except Exception as e:
    print(f"Error: {e}")

# # Tail logs in real-time
# for log in reader.tail_logs('/aws/lambda/test'):
#     print(f"{log.timestamp} [{log.log_stream}]: {log.message}")