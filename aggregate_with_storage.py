from log_aggregator import LogAggregator
from log_storage import LogStorage
from datetime import datetime, timedelta

# Initialize components
aggregator = LogAggregator(aws_region='us-east-1')
storage = LogStorage('logs.db')

# Define log sources
local_logs = [
    '/var/log/syslog',
    '/var/log/auth.log'
]

cloud_logs = [
    '/aws/lambda/test'
]

# Collect logs
all_logs = []

# Collect local logs
if local_logs:
    print("Collecting local logs...")
    local_entries = aggregator.collect_local_logs(
        log_paths=local_logs,
        is_json=False
    )
    all_logs.extend(local_entries)
    print(f"Collected {len(local_entries)} local log entries")

# Collect cloud logs
if cloud_logs:
    print("Collecting cloud logs...")
    cloud_entries = aggregator.collect_cloud_logs(
        log_groups=cloud_logs,
        hours_back=24
    )
    all_logs.extend(cloud_entries)
    print(f"Collected {len(list(cloud_entries))} cloud log entries")

# Print sample of logs before storage
print("\nSample of logs to be stored:")
for log in all_logs[:2]:
    print(f"Log entry: {log}")

# Store logs in SQLite
print(f"\nStoring {len(all_logs)} logs...")
storage.store_logs(all_logs)
print("Storage complete")

# Verify storage
with storage._get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM logs")
    log_count = cursor.fetchone()[0]
    print(f"\nTotal logs in database: {log_count}")

# Query example
recent_logs = storage.query_logs(
    start_time=datetime.now() - timedelta(hours=1),
    source_type='cloudwatch',
    limit=100
)

for log in recent_logs:
    print(f"[{log['timestamp']}] {log['source_name']}: {log['message']}") 