from enum import Enum


class CalendarStatus(Enum):
    """Enum representing the possible outcomes of a Google Calendar operation."""
    REVOKE = 0
    EMPTY = 1
    SUCCESS = 2


CREDENTIALS = "credentials"
FEATURES = "features"

LOCAL_TIME_ZONE = "America/Vancouver"  # Set your local timezone
TIME_FORMAT = "%H:%M"
DATE_FORMAT = "%Y-%m-%d"
DATE_TIME_FORMAT = DATE_FORMAT + " " + TIME_FORMAT

REDIS_TTL_VAL = 300 
REDIS_PAGINATE_KEY_FORMAT = ":paginate:"
REDIS_RECORD_KEY_FORMAT = ":record:"
REDIS_USER_ADDR_KEY_FORMAT = ":addr"