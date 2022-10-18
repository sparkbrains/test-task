"""
Developer: Jitender Verma
Database: sqlite3
Upwork Profile: https://www.upwork.com/freelancers/~014e12b8590255e158
Hourly Rate: 20 USD
Daily Possible Working Hours: 8 Hours
Timezone[Country]: India (Timezone: IST)
"""

from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from sql_app import models, schemas, crud
from sql_app.database import SessionLocal, engine
from slugify import slugify

from sql_app.enum import ActivityChoices
from utils import haversine

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

# Distance in kilometers, This is being used for comparing the location of events corresponding to the user.
DISTANCE_RADIUS = 10.00


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# User related apis
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Creation of a user
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.User])
def read_users(db: Session = Depends(get_db)):
    users = crud.get_users(db)
    return users


# Event related apis
@app.get("/events/", response_model=List[schemas.EventList])
def list_all_events(db: Session = Depends(get_db)):
    """
    Listing of all events
    """
    events = crud.list_all_events(db)
    return events


@app.get("/user-feed/", response_model=List[schemas.EventList])
def user_feed(email: str, db: Session = Depends(get_db)):
    """
    User feed
    """
    user = crud.get_user_by_email(db, email)

    if not user:
        raise HTTPException(status_code=400, detail="No user exists with the provided email")
    events = crud.list_all_events(db)
    suggested_events_generator = db.query(models.Activities).filter(and_(models.Activities.user == user.id,
                                                             or_(models.Activities.type == ActivityChoices.liked,
                                                                 models.Activities.type == ActivityChoices.played))).values(
        models.Activities.event)
    suggested_events_ids = [event[0] for event in suggested_events_generator]
    # Filtering events based on user location
    location_filtered_events = []
    user_latitude = user.latitude
    user_longitude = user.longitude
    for event in events:
        distance = haversine(user_longitude, user_latitude, event.longitude, event.latitude)
        if distance <= DISTANCE_RADIUS:
            location_filtered_events.append(event)
            if event.id in suggested_events_ids:
                suggested_events_ids.remove(event.id)
    # Filtering events based on user past liked events or played events
    if suggested_events_ids:
        suggested_events = crud.filter_events_by_ids(db, suggested_events_ids)
        location_filtered_events.extend(suggested_events)
    return location_filtered_events


@app.post("/event/create/", response_model=schemas.EventList)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    """
    Create an event which will be visible to all.
    """
    slug = slugify(event.title)
    db_event = crud.get_event_by_slug(db, slug=slug)
    if db_event:
        raise HTTPException(status_code=400, detail="Event already exists with the same title")
    check_user = crud.get_user_by_email(db, email=event.created_by)
    if not event.created_by or not check_user:
        raise HTTPException(status_code=400, detail="No user exists with the provided email")
    event.slug = slug
    event.created_by = check_user.id
    response = crud.create_event(db=db, event=event)
    return response


# Activity related apis
@app.post("/activity/create/", response_model=schemas.Activity)
def create_activity(activity: schemas.ActivityCreate, db: Session = Depends(get_db)):
    """
    Like an event or mark an event played.
    """
    event_obj = crud.get_event_by_slug(db, activity.event)
    if not event_obj:
        raise HTTPException(status_code=400, detail=f"No event exists with the provided slug")
    else:
        activity.event = event_obj.id
    user_obj = crud.get_user_by_email(db, activity.user)
    if not user_obj:
        raise HTTPException(status_code=400, detail=f"No user exists with the provided email")
    else:
        activity.user = user_obj.id
    check = crud.check_if_activity_exists(db, activity=activity)
    if check:
        raise HTTPException(status_code=400, detail=f"You have already {activity.type} this event")
    else:
        return crud.create_activity(db, activity=activity)
