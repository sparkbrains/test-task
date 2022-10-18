from sqlalchemy import Boolean, Column, Integer, String, Float, DateTime, ForeignKey

from .database import Base
from datetime import datetime


class User(Base):
    """
    General User model for saving the details of a user.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    latitude = Column(Float, default=0.00, nullable=True)
    longitude = Column(Float, default=0.00, nullable=True)
    is_active = Column(Boolean, default=True)


class Events(Base):
    """
    Events model for saving the information related to event
    """
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, default="")
    slug = Column(String, unique=True, index=True)
    start_date = Column(DateTime, default=datetime.now())
    end_date = Column(DateTime, default=datetime.now())
    created_by = Column(Integer, ForeignKey(User.id))
    latitude = Column(Float, default=0.00)
    longitude = Column(Float, default=0.00)


class Activities(Base):
    """
    This tables saves the information about the actvities of a user corresponding to the event.
    For e.g:
        If someone like the event or played the event then the entry will be saved in this model.
    """
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    user = Column(Integer, ForeignKey(User.id))
    event = Column(Integer, ForeignKey(Events.id))
    type = Column(String)

