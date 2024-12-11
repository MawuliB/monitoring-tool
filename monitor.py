import json
import os
import glob

# [Inspiration from [2] for structured log handling]
class Log:
    def __init__(self, file_path):
        self.file_path = file_path
        self.format = self.detect_format()

    def detect_format(self):
        # Basic format detection, extend as needed
        if self.file_path.endswith('.json'):
            return 'json'
        else:
            return 'plain_text'

    def read(self):
        if self.format == 'json':
            return self.read_json()
        elif self.format == 'plain_text':
            return self.read_plain_text()

    def read_json(self):
        try:
            with open(self.file_path, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            print(f"Failed to parse JSON in: {self.file_path}")
            return {}

    def read_plain_text(self):
        try:
            with open(self.file_path, 'r') as file:
                return file.readlines()
        except Exception as e:
            print(f"An error occurred reading plain text: {e}")
            return []

# [Combining concepts for a versatile log reader]
class LogReader:
    def __init__(self, directory, file_extension='.log'):
        self.directory = directory
        self.file_extension = file_extension

    def read_logs_recursively(self):
        logs = {'plain_text': [], 'json': []}
        for filename in glob.iglob(f"{self.directory}/**/*{self.file_extension}", recursive=True):
            file_path = os.path.abspath(filename)
            log = Log(file_path)
            content = log.read()
            if log.format == 'json':
                logs['json'].append((file_path, content))
            else:
                logs['plain_text'].append((file_path, content))
        return logs

    # [Inspired by batch processing in [2]]
    def process_logs(self, logs, processor=None):
        if processor:
            processed_logs = []
            for log_type in logs.values():
                for file_path, content in log_type:
                    processed_logs.append(processor(content))
            return processed_logs
        else:
            return logs

# Example Usage
if __name__ == "__main__":
    directory = '/var/log'  # For Linux
    # directory = 'C:/Logs'  # For Windows, adjust as necessary
    reader = LogReader(directory)
    logs = reader.read_logs_recursively()
    
    print("Plain Text Logs:")
    for path, content in logs['plain_text']:
        print(f"File: {path}")
        print(content)
        
    print("\nJSON Logs:")
    for path, content in logs['json']:
        print(f"File: {path}")
        print(content)

        
    # Example processor for JSON logs (e.g., extracting a specific field)
    def process_json_log(log_content):
        return log_content.get('INFO', 'Not Found')
        
    processed_json_logs = reader.process_logs({'json': logs['plain_text']}, processor=process_json_log)
    print("\nProcessed JSON Logs (Example):")
    for log in processed_json_logs:
        print(log)