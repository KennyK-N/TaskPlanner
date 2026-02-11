from zoneinfo import ZoneInfo 
import datetime  
from dateutil import parser

from .general_utils import (
    LOCAL_TIME_ZONE,
    DATE_TIME_FORMAT
)

def convert_HHMM_to_iso_datetime(date, HHMM):
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