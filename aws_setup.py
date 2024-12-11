from auth import AuthManager
import os
from dotenv import load_dotenv

load_dotenv()

# Option 1: Use access keys
auth = AuthManager()
session = auth.get_aws_session(
    aws_access_key=os.getenv('ACCESS'),
    aws_secret_key=os.getenv('SECRET')
)