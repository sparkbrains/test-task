from datetime import datetime
from typing import List, Union, Literal

from pydantic import BaseModel, Field

from sql_app.enum import ActivityChoices


# User related schemas
class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str
    latitude: float
    longitude: float


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True


# Event related schemas
class EventBase(BaseModel):
    title: str
    start_date: Union[datetime, None] = None
    end_date: Union[datetime, None] = None


class EventList(EventBase):
    id: int
    slug: str

    class Config:
        orm_mode = True


class EventCreate(EventBase):
    slug: Union[str, None] = None
    created_by: str = Field(title="Email of the user")
    latitude: float
    longitude: float


# Activity related schemas
class ActivityBase(BaseModel):
    user: str = Field(title='Email of the user')
    event: str = Field(title='Unique Slug of the event')
    type: ActivityChoices


class ActivityCreate(ActivityBase):
    pass


class Activity(ActivityBase):
    user: int
    event: int
    type: str
    id: int

    class Config:
        orm_mode = True
