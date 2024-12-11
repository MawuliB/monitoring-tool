from typing import Optional, Dict
import boto3
import json
import os
from pathlib import Path
import click
from datetime import datetime, timedelta
import jwt
from functools import wraps

class AuthManager:
    """Manages authentication and authorization for log access."""
    
    def __init__(self, config_path: str = 'auth_config.json'):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._session = None
    
    def _load_config(self) -> Dict:
        """Load authentication configuration."""
        if not self.config_path.exists():
            default_config = {
                'jwt_secret': os.urandom(32).hex(),
                'token_expiry_hours': 24,
                'allowed_users': {}
            }
            self.config_path.write_text(json.dumps(default_config, indent=2))
            return default_config
        
        return json.loads(self.config_path.read_text())
    
    def create_user(self, username: str, role: str = 'reader') -> str:
        """Create a new user and return their access token."""
        if username in self.config['allowed_users']:
            raise ValueError(f"User {username} already exists")
        
        # Generate token
        token = self._generate_token(username, role)
        
        # Store user info
        self.config['allowed_users'][username] = {
            'role': role,
            'created_at': datetime.now().isoformat()
        }
        
        # Save config
        self.config_path.write_text(json.dumps(self.config, indent=2))
        return token
    
    def _generate_token(self, username: str, role: str) -> str:
        """Generate JWT token for user."""
        expiry = datetime.now() + timedelta(hours=self.config['token_expiry_hours'])
        payload = {
            'username': username,
            'role': role,
            'exp': expiry
        }
        return jwt.encode(payload, self.config['jwt_secret'], algorithm='HS256')
    
    def verify_token(self, token: str) -> Dict:
        """Verify JWT token and return payload."""
        try:
            return jwt.decode(token, self.config['jwt_secret'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
    
    def get_aws_session(
        self,
        aws_access_key: Optional[str] = None,
        aws_secret_key: Optional[str] = None,
        aws_role_arn: Optional[str] = None
    ) -> boto3.Session:
        """Get or create AWS session with appropriate credentials."""
        if self._session:
            return self._session
            
        if aws_access_key and aws_secret_key:
            # Use provided credentials
            self._session = boto3.Session(
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key
            )
        elif aws_role_arn:
            # Assume role
            sts = boto3.client('sts')
            response = sts.assume_role(
                RoleArn=aws_role_arn,
                RoleSessionName='LogQuerySession'
            )
            credentials = response['Credentials']
            self._session = boto3.Session(
                aws_access_key_id=credentials['AccessKeyId'],
                aws_secret_access_key=credentials['SecretAccessKey'],
                aws_session_token=credentials['SessionToken']
            )
        else:
            # Try default credentials
            self._session = boto3.Session()
            
        return self._session

def requires_auth(f):
    """Decorator to require authentication for CLI commands."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = os.environ.get('LOG_QUERY_TOKEN')
        if not token:
            raise click.ClickException(
                "Authentication required. Please set LOG_QUERY_TOKEN environment variable."
            )
        
        try:
            auth = AuthManager()
            auth.verify_token(token)
        except ValueError as e:
            raise click.ClickException(str(e))
            
        return f(*args, **kwargs)
    return decorated
