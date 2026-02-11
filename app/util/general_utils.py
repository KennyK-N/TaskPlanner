from enum import Enum


class CalendarStatus(Enum):
    REVOKE = 0
    EMPTY = 1
    SUCCESS = 2


CREDENTIALS = "credentials"
FEATURES = "features"

LOCAL_TIME_ZONE = "America/Vancouver"  # Set your local timezone
TIME_FORMAT = "%H:%M"
DATE_FORMAT = "%Y-%m-%d"
DATE_TIME_FORMAT = DATE_FORMAT + " " + TIME_FORMAT
