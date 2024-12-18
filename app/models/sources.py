from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..database import Base

class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # e.g., 'aws', 'local', etc.
    configuration = Column(String)  # JSON string for source-specific configuration
    
    logs = relationship("Log", back_populates="source")
