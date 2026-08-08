from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime

from database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    source_type = Column(String, nullable=False)
    artifacts_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)