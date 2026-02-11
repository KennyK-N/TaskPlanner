import google.oauth2.credentials
import googleapiclient.discovery
import json

from flask import session
from app.auth.config import OAUTH_INFO
from app.util import *


def create_calendar(task_list, date):
  client_config = OAUTH_INFO["CLIENT_SECRETS_FILE"]["web"]
  session_credentials = session['credentials']

  try:
    if not isinstance(task_list, list):
      task_list = json.loads(task_list)
    
    credentials = google.oauth2.credentials.Credentials(
        refresh_token=session_credentials.get('refresh_token'),
        scopes=session_credentials.get('granted_scopes'),
        token=session_credentials.get('token'),
        client_id=client_config.get('client_id'),
        client_secret=client_config.get('client_secret'),
        token_uri=client_config.get('token_uri'))
    
    if credentials.expired and not credentials.refresh_token:
      return general_utils.CalendarStatus.REVOKE
    
    service = googleapiclient.discovery.build(
        OAUTH_INFO["API_SERVICE_NAME"], OAUTH_INFO["API_VERSION"], credentials=credentials)
    
    for task in task_list:
      begin_time = time_conversion_utils.convert_HHMM_to_iso_datetime(date, task['time_begin'])

      end_time = time_conversion_utils.convert_HHMM_to_iso_datetime(date, task['time_end'])

      if begin_time is None or end_time is None:
        continue

      event = {
        'summary': task['task_name'],
        'description': task['description'],
        'start': {
          'dateTime': begin_time,
          'timeZone': general_utils.LOCAL_TIME_ZONE,
        },
        'end': {
          'dateTime': end_time,
          'timeZone': general_utils.LOCAL_TIME_ZONE,
        }
      }

      if task['location'].lower() not in [' ', '', 'none']:
        event['location'] = task['location']

      event = service.events().insert(calendarId='primary', body=event).execute()
      print ('Event created: %s' % (event.get('htmlLink')))

    return general_utils.CalendarStatus.SUCCESS
  except Exception as exception:
    print(exception)
    return general_utils.CalendarStatus.EMPTY
