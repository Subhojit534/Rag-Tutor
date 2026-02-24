"""
System Models - Audit Logs and Settings
"""
from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey, TIMESTAMP, text
from sqlalchemy.orm import relationship
from app.database import Base


class AuditLog(Base):
    """Audit log for admin actions."""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(255), nullable=False)
    entity = Column(String(100), nullable=False, index=True)
    entity_id = Column(Integer, nullable=True)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, entity={self.entity})>"


class SystemSetting(Base):
    """System-wide settings (exam mode, rate limits, etc.)."""
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    setting_key = Column(String(100), unique=True, nullable=False)
    setting_value = Column(String(500), nullable=False)
    description = Column(String(255), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_at = Column(
        TIMESTAMP, 
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
    )
    
    def __repr__(self):
        return f"<SystemSetting(key={self.setting_key}, value={self.setting_value})>"
