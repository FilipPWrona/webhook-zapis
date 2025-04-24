from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class FormSubmission(Base):
    """Model dla danych przesłanych z formularza."""
    __tablename__ = "form_submissions"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    form_id = Column(String(255), index=True)
    form_name = Column(String(255))
    form_data = Column(JSON)  # Przechowuje wszystkie dane formularza jako JSON
    notified = Column(Boolean, default=False)  # Czy powiadomienie zostało wysłane
    notification_sent_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<FormSubmission(id={self.id}, form_id={self.form_id})>"

class Notification(Base):
    """Model dla wysłanych powiadomień."""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    submission_id = Column(Integer, index=True)
    recipient = Column(String(255))
    subject = Column(String(255))
    message = Column(Text)
    status = Column(String(50))  # np. "sent", "failed", "pending"
    error_message = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Notification(id={self.id}, status={self.status})>" 