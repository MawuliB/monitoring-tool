from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("sources.id"))
    timestamp = Column(DateTime, nullable=False)
    level = Column(String)
    message = Column(String, nullable=False)
    
    source = relationship("Source", back_populates="logs") 