from enum import Enum


class ActivityChoices(str, Enum):
    liked = 'liked'
    played = 'played'

class EventCategory(str, Enum):
    tournament = 'tournament'
