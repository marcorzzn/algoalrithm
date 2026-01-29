from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from backend.data.database.database import Base
import uuid
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    subscription_tier = Column(String(50), default="free")  # free, pro, enterprise
    
    # Betting settings
    betting_config = Column(JSON, default={
        "initial_bankroll": 1000,
        "max_stake": 0.05,
        "kelly_fraction": 0.25
    })
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)