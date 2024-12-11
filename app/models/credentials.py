from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base
from cryptography.fernet import Fernet
import os

# Encryption key (in production, store this securely)
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
cipher_suite = Fernet(ENCRYPTION_KEY)

class Credential(Base):
    __tablename__ = "credentials"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    platform = Column(String)
    encrypted_data = Column(String)
    
    def set_credentials(self, data: dict):
        """Encrypt credentials before storing"""
        encrypted = cipher_suite.encrypt(str(data).encode())
        self.encrypted_data = encrypted.decode()
    
    def get_credentials(self) -> dict:
        """Decrypt stored credentials"""
        decrypted = cipher_suite.decrypt(self.encrypted_data.encode())
        return eval(decrypted.decode()) 