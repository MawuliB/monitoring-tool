from log_aggregator import LogAggregator

# Initialize aggregator
aggregator = LogAggregator(aws_region='us-east-1')

# Define log sources
local_logs = [
    '/var/log/syslog',
    '/var/log/auth.log'
]

cloud_logs = [
    '/aws/lambda/test'
]

# Aggregate logs
aggregator.aggregate_logs(
    local_paths=local_logs,
    cloud_groups=cloud_logs,
    output_file='aggregated_logs.json',
    hours_back=24,  # Get last 24 hours of cloud logs
    local_is_json=False
) 