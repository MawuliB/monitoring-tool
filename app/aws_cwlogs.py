# NEW FIX
import os
import boto3
import logging
from flask import Flask, jsonify, request
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

# Flask app initialization
app = Flask(__name__)

# AWS credentials from environment variables
AWS_REGION = 'eu-west-2'
AWS_ACCESS_KEY = os.getenv('ACCESS_KEYS')
AWS_SECRET_KEY = os.getenv('SECRET_KEYS')

# CloudWatch log group and stream names
LOG_GROUP_NAME = 'app.log'
LOG_STREAM_NAME = 'i-01071eb2724f085ec'

# Boto3 client for CloudWatch
client = boto3.client(
    'logs',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
)


# GET ALL LOGS FROM A LOG GROUP AND STREAM
@app.route('/logs', methods=['GET'])
def get_logs():
    try:
        # Parse optional query parameters for time filtering
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        
        if not start_time or not end_time:
            return jsonify({'error': 'Missing required parameters: start_time and end_time'}), 400

        # Convert timestamps from ISO 8601 to milliseconds
        start_time_ms = int(datetime.fromisoformat(start_time).timestamp() * 1000)
        end_time_ms = int(datetime.fromisoformat(end_time).timestamp() * 1000)

        # Fetch logs from CloudWatch
        response = client.filter_log_events(
            logGroupName=LOG_GROUP_NAME,
            logStreamNames=[LOG_STREAM_NAME],
            startTime=start_time_ms,
            endTime=end_time_ms,
        )

        # Format logs
        events = response.get('events', [])
        logs = [
            {
                "timestamp": datetime.fromtimestamp(e['timestamp'] / 1000, tz=timezone.utc).isoformat(),
                "message": e['message'],
            }
            for e in events
        ]

        return jsonify({'logs': logs})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
# fetch logs by log levels
def fetch_logs_by_level(log_level):
    try: 
        response = client.filter_log_event(
            logGroupName=LOG_GROUP_NAME,
            logStreamName=LOG_STREAM_NAME,
            filterPattern=log_level if log_level else 'INFO'
#            # startFromHead=True,
        #     startTime=logs[0]['timestamp'],
        #     endTime=logs[-1]['timestamp'],
        #     filterPattern=f'[{level}]'
         )
        logs = response.get('events', [])
        filtered_logs = []
        for event in logs:
            if log_level:
                if log_level.upper() in event["message"].uppper():
                    filtered_logs.append(event)
            else:
                filtered_logs.append(event)
        return filtered_logs
    except Exception as e:
        logging.error(f"Failed to fetch logs: {str(e)}")
        return []
    
    
# # GET LOGS BY LEVEL
# @app.route('/logs/level', methods=['GET'])
# def get_logs_by_level():
#     log_level = request.args.get('log_level')
#     logs = fetch_logs_by_level(log_level)
#     formatted_logs = [
#         {
#             'timestamp': datetime.fromtimestamp(event['timestamp'] / 1000).isoformat(),
#             'message': event['message'],
#         }
#         for event in logs
#     ]
#     return jsonify({'logs': formatted_logs})

# NEW FIX
@app.route('/log_level', methods=['GET'])
def get_logs_level():
    log_level = request.args.get('log_level', 'INFO')  # Default to 'INFO'
    try:
        response = client.filter_log_events(
            logGroupName=LOG_GROUP_NAME,
            logStreamNames=[LOG_STREAM_NAME],
            filterPattern=log_level
        )
        events = response.get('events', [])
        logs = [
            {"timestamp": e["timestamp"], "message": e["message"]}
            for e in events
        ]
        return jsonify({"logs": logs})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)


# add log level to also filter by time and log level
# a file path that contains the logs and reads the file to get the logs
# eg. 