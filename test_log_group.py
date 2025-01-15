import os
import boto3

# session = boto3.Session(profile_name="max-user-iam"
#     # aws_access_key_id=os.getenv("ACCESS_KEYS"),
#     # aws_secret_access_key=os.getenv("SECRET_KEY"),
#     # region_name="eu-west-2"
#     )

client = boto3.client(
    "logs",
    aws_access_key_id=os.getenv("ACCESS_KEYS"),
    aws_secret_access_key=os.getenv("SECRET_KEYS"),
    region_name="eu-west-2"
)

# Example: List log groups
response = client.describe_log_groups()
print(response)
