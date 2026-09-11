from sqlalchemy import Column, String, Integer, JSON, DateTime,Text,ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
import uuid

from database import Base


DEFAULT_POLICY = {
    "remote_raw_pii": False,
    "remote_unsanitized_image": False,
    "high_risk_confirmation": True
}


class Session(Base):
    __tablename__ = "sessions"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    session_id = Column(
        String(100),
        unique=True,
        nullable=False,
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

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime,
        onupdate=func.now(),
        nullable=True
    )


class Observation(Base):
    __tablename__ = "observations"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    observation_id = Column(
        String(100),
        unique=True,
        nullable=False
    )

    session_id = Column(
        String(100),
        ForeignKey("sessions.session_id"),
        nullable=False
    )

    url = Column(
        JSONB,
        nullable=False
    )

    page = Column(
        JSONB,
        nullable=False
    )

    dom_elements = Column(
        ARRAY(JSONB),
        nullable=False
    )

    ocr_text_blocks = Column(
        ARRAY(JSONB),
        nullable=False
    )

    screenshot = Column(
        Text,
        nullable=True
    )

    detected_redaction_types = Column(
        ARRAY(String),
        nullable=False
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime,
        onupdate=func.now(),
        nullable=True
    )


class Context(Base):
    __tablename__ = "contexts"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    context_id = Column(
        String(100),
        unique=True,
        nullable=False,
        default=lambda: f"ctx_{uuid.uuid4().hex}"
    )

    observation_id = Column(
        String(100),
        ForeignKey("observations.observation_id"),
        nullable=False
    )

    allowed_actions = Column(
        ARRAY(String),
        nullable=True
    )

    require_confirmation_for = Column(
        ARRAY(String),
        nullable=True
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime,
        onupdate=func.now(),
        nullable=True
    )
