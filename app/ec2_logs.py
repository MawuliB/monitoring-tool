# import os
# import boto3
# from flask import Flask, jsonify, request
# from dotenv import load_dotenv

# load_dotenv()

# app = Flask(__name__)

# AWS_REGION = os.getenv('AWS_REGION')
# AWS_ACCESS_KEY = os.getenv('ACCESS_KEYS')
# AWS_SECRET_KEY = os.getenv('SECRET_KEYS')
# LOG_GROUP_NAME = os.getenv("LOG_GROUP_NAME")
# LOG_STREAM_NAME = os.getenv("LOG_STREAM_NAME")

# client = boto3.client('logs', 
#                       region_name=AWS_REGION, 
#                       aws_access_key_id=AWS_ACCESS_KEY, 
#                       aws_secret_access_key=AWS_SECRET_KEY)

# @app.route('/logs', methods=['GET'])
# def get_logs():
#     try:
#         # Fetch logs
#         response = client.get_log_events(
#             logGroupName=LOG_GROUP_NAME,
#             logStreamName=LOG_STREAM_NAME,
#             startFromHead=True  # Fetch from start
#         )
#         events = response.get("events", [])
#         # Format logs
#         logs = [{"timestamp": e["timestamp"], "message": e["message"]} for e in events]
#         return jsonify({"logs": logs})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# if __name__ == "__main__":
#     app.run(debug=True, host="0.0.0.0", port=5000)

# import os
# import boto3
# from flask import Flask, jsonify, request
# from dotenv import load_dotenv
# from datetime import datetime, timedelta

# load_dotenv()

# app = Flask(__name__)

# AWS_REGION = 'eu-west-2'
# AWS_ACCESS_KEY = os.getenv('ACCESS_KEYS')
# AWS_SECRET_KEY = os.getenv('SECRET_KEYS')
# LOG_GROUP_NAME = 'Ec2LogData'
# LOG_STREAM_NAME = 'Ec2Logs'

# client = boto3.client('logs', 
#                       region_name=AWS_REGION, 
#                       aws_access_key_id=AWS_ACCESS_KEY, 
#                       aws_secret_access_key=AWS_SECRET_KEY)

# @app.route('/logs', methods=['GET'])
# def get_logs():
#     try:
#         start_time = request.args.get('start_time')
#         end_time = request.args.get('end_time')

#         if not start_time or not end_time:
#             return jsonify({'error': 'Missing required parameters: start_time and end_time'}), 400

#         start_time = datetime.fromisoformat(start_time)
#         end_time = datetime.fromisoformat(end_time)

#         response = client.filter_log_events(
#             logGroupName=LOG_GROUP_NAME,
#             logStreamNames=[LOG_STREAM_NAME],
#             startTime=int(start_time.timestamp() * 1000),
#             endTime=int(end_time.timestamp() * 1000)
#         )
#         events = response.get("events", [])
#         logs = [{"timestamp": datetime.fromtimestamp(e["timestamp"] / 1000).isoformat(), "message": e["message"]} for e in events]
#         return jsonify({"logs": logs})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# if __name__ == "__main__":
#     app.run(debug=True, host="0.0.0.0", port=5000)


# import os
# import boto3
# from flask import Flask, jsonify, request, send_file
# from dotenv import load_dotenv
# from datetime import datetime, timedelta
# import json

# load_dotenv()

# app = Flask(__name__)

# AWS_REGION = 'eu-west-2'
# AWS_ACCESS_KEY = os.getenv('ACCESS_KEYS')
# AWS_SECRET_KEY = os.getenv('SECRET_KEYS')
# LOG_GROUP_NAME = 'Ec2LogData'
# LOG_STREAM_NAME = 'Ec2Logs'

# client = boto3.client('logs', 
#                       region_name=AWS_REGION, 
#                       aws_access_key_id=AWS_ACCESS_KEY, 
#                       aws_secret_access_key=AWS_SECRET_KEY)

# @app.route('/logs', methods=['GET'])
# def get_logs():
#     try:
#         # Get query parameters for start and end times
#         start_time = request.args.get('start_time')
#         end_time = request.args.get('end_time')

#         if not start_time or not end_time:
#             return jsonify({'error': 'Missing required parameters: start_time and end_time'}), 400

#         # Convert time strings to datetime objects
#         start_time = datetime.fromisoformat(start_time)
#         end_time = datetime.fromisoformat(end_time)

#         # Fetch logs
#         response = client.filter_log_events(
#             logGroupName=LOG_GROUP_NAME,
#             logStreamNames=[LOG_STREAM_NAME],
#             startTime=int(start_time.timestamp() * 1000),
#             endTime=int(end_time.timestamp() * 1000)
#         )
        
#         # Extract and format logs
#         events = response.get("events", [])
#         logs = [
#             {
#                 "timestamp": datetime.fromtimestamp(e["timestamp"] / 1000).isoformat(),
#                  "message": e["message"]
#             } 
#             for e in events
#             ]

#         # # Save logs to a JSON file
#         # log_file_path = "logs.json"
#         # with open(log_file_path, "w") as log_file:
#         #     json.dump(logs, log_file, indent=4)

#         # Serve the file for download
#         # return send_file(log_file_path, as_attachment=True)
#         return send_file()
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# if __name__ == "__main__":
#     app.run(debug=True, host="0.0.0.0", port=5000)


import os
import boto3
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

AWS_REGION = 'eu-west-2'
AWS_ACCESS_KEY = os.getenv('ACCESS_KEYS')
AWS_SECRET_KEY = os.getenv('SECRET_KEYS')
LOG_GROUP_NAME = 'CloudsLogGroup'   #'Ec2LogData'
LOG_STREAM_NAME = 'Ec2Logs'

# Initialize the CloudWatch Logs client
client = boto3.client('logs', 
                      region_name=AWS_REGION, 
                      aws_access_key_id=AWS_ACCESS_KEY, 
                      aws_secret_access_key=AWS_SECRET_KEY)

@app.route('/logs', methods=['GET'])
def get_logs():
    try:
        # Fetch start_time and end_time from query parameters
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')

        # Validate required parameters
        if not start_time or not end_time:
            return jsonify({'error': 'Missing required parameters: start_time and end_time'}), 400

        # Convert ISO string times to timestamps
        start_time = datetime.fromisoformat(start_time)
        end_time = datetime.fromisoformat(end_time)

        # Fetch logs from CloudWatch Logs
        response = client.filter_log_events(
            logGroupName=LOG_GROUP_NAME,
            # logStreamNames=[LOG_STREAM_NAME],
            startTime=int(start_time.timestamp() * 1000),
            endTime=int(end_time.timestamp() * 1000)
        )

        # Extract and format log events
        events = response.get("events", [])
        logs = [
            {
                "timestamp": datetime.fromtimestamp(e["timestamp"] / 1000).isoformat(),
                "message": e["message"]
            }
            for e in events
        ]

        # Return the logs as JSON response
        return jsonify({"logs": logs})

    except Exception as e:
        # Handle any errors
        return jsonify({"error": str(e)}), 500


@app.route('/instance-logs', methods=['GET'])
def get_instance_logs():
    try:
        # Fetch instance_id, start_time, and end_time from query parameters
        instance_id = request.args.get('instance_id')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')

        # Validate required parameters
        if not instance_id or not start_time or not end_time:
            return jsonify({'error': 'Missing required parameters: instance_id, start_time, and end_time'}), 400

        # Convert ISO string times to timestamps
        start_time = datetime.fromisoformat(start_time)
        end_time = datetime.fromisoformat(end_time)

        # Fetch logs from CloudWatch Logs
        response = client.filter_log_events(
            logGroupName=LOG_GROUP_NAME,
            filterPattern=f'"{instance_id}"',
            startTime=int(start_time.timestamp() * 1000),
            endTime=int(end_time.timestamp() * 1000)
        )

        # Extract and format log events
        events = response.get("events", [])
        logs = [
            {
                "timestamp": datetime.fromtimestamp(e["timestamp"] / 1000).isoformat(),
                "message": e["message"]
            }
            for e in events
        ]

        # Print logs to console for testing
        for log in logs:
            print(log)

        # Return the logs as JSON response
        return jsonify({"logs": logs})

    except Exception as e:
        # Handle any errors
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    # Run the Flask app
    app.run(debug=True, host="0.0.0.0", port=5000)
