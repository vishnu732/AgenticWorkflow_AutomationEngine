from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.database.db import Base


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(String, unique=True, index=True, nullable=False)
    original_process = Column(Text, nullable=False)
    status = Column(String, nullable=False)
    steps_json = Column(Text, nullable=False)
    audit_log_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)