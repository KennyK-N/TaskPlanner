from zoneinfo import ZoneInfo
import datetime
from dateutil import parser

from .general_utils import LOCAL_TIME_ZONE, DATE_TIME_FORMAT


def convert_HHMM_to_iso_datetime(date, HHMM):
    """
    Combines a date string and HH:MM time, converts it to an ISO 8601 string in the local timezone.
    Args:
        date (str): Date string e.g. "2025-01-01"
        HHMM (str): Time string e.g. "09:00"
    Returns:
        str: ISO 8601 datetime string with local timezone offset, or None if parsing fails.
    """
    try:
        date_time = date + " " + HHMM
        date_time = datetime.datetime.strptime(date_time, DATE_TIME_FORMAT)

        iso_dt_utc = date_time.isoformat()
        iso_dt_utc = datetime.datetime.fromisoformat(iso_dt_utc)

        local_tz = ZoneInfo(LOCAL_TIME_ZONE)
        iso_dt_tz = iso_dt_utc.astimezone(local_tz)
        iso_dt_tz = iso_dt_tz.isoformat()

        return iso_dt_tz
    except Exception as exception:
        print(exception)
        return None


def utc_to_local_timezone(date):

    """
    Converts a UTC datetime to a human-readable local time string.
    Args:
        date (datetime | str): Accepts either a datetime object or an ISO format string.
    Returns:
        str: Formatted date string like "2025-01-01 09:00 AM", or None if parsing fails.
    """
    try:
        if isinstance(date, datetime.datetime):
            date = date.isoformat()

        dt_utc = parser.parse(date)
        local_tz = ZoneInfo(LOCAL_TIME_ZONE)
        dt_local = dt_utc.astimezone(local_tz)

        formatted_date = dt_local.strftime("%Y-%m-%d %I:%M %p")
        return formatted_date
    except Exception as exception:
        print(exception)
        return None
