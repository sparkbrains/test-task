from sqlalchemy.orm import Session
from sqlalchemy import and_

from . import models, schemas
from datetime import datetime


# User related operations
def get_users(db: Session):
    return db.query(models.User).all()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password, latitude=user.latitude,
                          longitude=user.longitude)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Event related operations
def get_event_by_slug(db: Session, slug: str):
    return db.query(models.Events).filter(models.Events.slug == slug).first()


def create_event(db: Session, event: schemas.EventCreate):
    db_event = models.Events(title=event.title, slug=event.slug, start_date=event.start_date, end_date=event.end_date,
                             created_by=event.created_by, latitude=event.latitude, longitude=event.longitude)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


def list_all_events(db: Session):
    today = datetime.now()
    return db.query(models.Events).filter(models.Events.end_date > today).all()


def filter_events_by_ids(db: Session, ids: list):
    return db.query(models.Events).filter(models.Events.id.in_(ids))


# Activity Related Operations
def create_activity(db: Session, activity: schemas.ActivityCreate):
    db_activity_obj = models.Activities(user=activity.user, event=activity.event, type=activity.type)
    db.add(db_activity_obj)
    db.commit()
    db.refresh(db_activity_obj)
    return db_activity_obj


def check_if_activity_exists(db: Session, activity: schemas.ActivityCreate):
    check_activity = db.query(models.Activities).filter(models.Activities.user == activity.user,
                                                        models.Activities.event == activity.event).filter(
        models.Activities.type == activity.type).first()
    return check_activity


def list_activities(db: Session, user: int):
    return db.query(models.Activities).filter(models.Activities.user == user)
