from sqlalchemy import Column, String, Integer, JSON, DateTime
from sqlalchemy.sql import func
import uuid
from database import Base


DEFAULT_POLICY = {
    "remote_raw_pii": False,
    "remote_unsanitized_image": False,
    "high_risk_confirmation": True
}


class Session(Base):

    __tablename__ = "sessions"

    session_id = Column(
        String(100),
        primary_key=True,
        default=lambda: f"sess_{uuid.uuid4().hex}"
    )

    client_version = Column(String(50), nullable=False)
    browser = Column(String(50), nullable=False)

    status = Column(String(30), nullable=False)
    expires_in = Column(Integer, nullable=False)

    policy = Column(
        JSON,
        default=lambda: DEFAULT_POLICY.copy(),
        nullable=False
    )

    createdAt = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    updatedAt = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
