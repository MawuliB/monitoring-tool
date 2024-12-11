from log_reader import *

# Example 1: Reading a plain text log file
log_reader = LogReader("/var/log/syslog")
for entry in log_reader.read_plain_text():
    print(f"Timestamp: {entry['timestamp']}, Message: {entry['message']}")

# Example 2: Reading a JSON log file
json_log_reader = LogReader("/var/log/auth.log")
for entry in json_log_reader.read_json():
    print(f"Log Entry: {entry}")

# Example 3: Finding all log files in a directory
system_logs = get_system_logs()
for log_dir in system_logs:
    log_files = LogReader.find_logs(log_dir)
    print(f"Found logs in {log_dir}: {log_files}")