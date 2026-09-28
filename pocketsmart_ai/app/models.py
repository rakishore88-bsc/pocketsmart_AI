from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)

from .database import Base


class User(Base):
    """
    Stores registered PocketSmart AI users.
    """

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    username = Column(
        String(80),
        unique=True,
        index=True,
        nullable=False,
    )

    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash = Column(
        String(255),
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


class RecommendationHistory(Base):
    """
    Stores the user's generated recommendation history.

    The request and response are stored as JSON strings so that
    the complete AI recommendation can be retrieved later.
    """

    __tablename__ = "recommendation_history"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        index=True,
        nullable=False,
    )

    category = Column(
        String(30),
        nullable=False,
    )

    budget = Column(
        Float,
        nullable=False,
    )

    request_json = Column(
        Text,
        nullable=False,
    )

    response_json = Column(
        Text,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )