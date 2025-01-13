import os
import boto3
from flask import Flask, jsonify, request

# load_dotenv()

app = Flask(__name__)

AWS_REGION = os.getenv('AWS_REGION')
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
LOG_GROUP_NAME = '/aws/lambda/my-lambda-function'
LOG_STREAM_NAME = '2021/07/01/[$LATEST]1234567890abcdef'

client = boto3.client('logs', 
                      region_name=AWS_REGION, 
                      aws_access_key_id=AWS_ACCESS_KEY, 
                      aws_secret_access_key=AWS_SECRET_KEY)

app.route('/logs', methods=['GET'])
def get_logs():
    try:
        # Fetch logs
        response = client.get_log_events(
            logGroupName=LOG_GROUP_NAME,
            logStreamName=LOG_STREAM_NAME,
            startFromHead=True  # Fetch from start
        )
        events = response.get("events", [])
        # Format logs
        logs = [{"timestamp": e["timestamp"], "message": e["message"]} for e in events]
        return jsonify({"logs": logs})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)