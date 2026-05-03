import pytest
from app.api import *
from unittest.mock import MagicMock
from app.api.Geocoding import geocoding_
from app.util import *

def test_get_addr_success(mocker, mock_geocoding_profile_id, mock_geocoding_redis_get):
    """Geocoder finds a location and Nominatim reverses it to a real address string."""
    nominatim_mock = mocker.patch.object(geocoding_, "Nominatim")
    mocker.patch.object(geocoding_, "geocoder")
    
    mock_geocoding_redis_get(None)
    mocker.patch.object(geocoding_, "redis_set")
    
    mock_location = mocker.Mock()
    mock_location.address = "123 Test St"
    
    nominatim_mock.return_value.reverse.return_value = mock_location
   
    response = geocoding_.get_addr()
    
    assert response == "123 Test St"

def test_get_addr_success_redis(mocker, mock_geocoding_profile_id, mock_geocoding_redis_get):
    """Address is already cached in Redis so Nominatim is never called."""
    mocker.patch.object(geocoding_, "Nominatim")
    mocker.patch.object(geocoding_, "geocoder")
    
    mock_geocoding_redis_get("123 Test St")
    
    response = geocoding_.get_addr()
   
    assert response == "123 Test St"

def test_get_addr_fail(mocker, mock_geocoding_profile_id, mock_geocoding_redis_get):
    """Geocoder IP lookup fails (ok=False) so None is returned."""
    mock_geo = MagicMock()
    mock_geo.ok = False
    
    mock_geocoding_redis_get(None)
    
    mocker.patch.object(geocoding_.geocoder, "ip", return_value=mock_geo)
    
    response = geocoding_.get_addr()
    
    assert response == None


def test_gemini_prompt_success(mocker, flask_app_mock):
    """Gemini returns valid JSON text which gets parsed and returned as a dict."""
    from app.api.Gemini import gemini_
    flask_app_mock.extensions["gemini_CLIENT"].models.generate_content.return_value.text = '{"1": 1}'
    with flask_app_mock.app_context():
        response = gemini_.generate_tasks("test", "test")
        assert response == {"1": 1}

def test_gemini_prompt_fail(mocker, flask_app_mock):
    """Gemini raises an exception so generate_tasks returns None."""
    from app.api.Gemini import gemini_

    flask_app_mock.extensions["gemini_CLIENT"].models.generate_content.side_effect = Exception("Failed to Generate Prompt")
    
    with flask_app_mock.app_context():
        response = gemini_.generate_tasks("test", "test")
        assert response == None

def test_calendar_success(mocker):
    """Valid task list with good times creates a calendar event and returns SUCCESS."""
    date = "2025-02-05"
    task_list = [{
        "time_begin": "13:00",
        "time_end": "15:00",
        "task_name": "Test",
        "description": "Testing description",
        "location": "Vancouver"
    }]
    oauth_mock = mocker.patch("app.api.Google_Calendar.google_calendar_.google.oauth2.credentials.Credentials")
    mocker.patch("app.api.Google_Calendar.google_calendar_.session", {"credentials": MagicMock()})
    oauth_mock.return_value = MagicMock()
    oauth_mock.expired == False
    oauth_mock.refresh_token == False

    service_mock = mocker.patch("app.api.Google_Calendar.google_calendar_.googleapiclient.discovery", return_value = MagicMock())
    service_mock.build.return_value.events.return_value.insert.return_value.execute.return_value = MagicMock()
    service_mock.events.insert.execute.get.return_value = "Testing Works"

    response = google_calendar_.create_calendar(task_list,date)
    assert response == general_utils.CalendarStatus.SUCCESS

def test_calendar_fail_invalid_input(mocker):
    """Passing a dict instead of a list for task_list causes json.loads to fail and returns EMPTY."""
    date = "2025-02-05"
    task_list = {
        "time_begin": "13:00",
        "time_end": "15:00",
        "task_name": "Test",
        "description": "Testing description",
        "location": "Vancouver"
    }
    oauth_mock = mocker.patch("app.api.Google_Calendar.google_calendar_.google.oauth2.credentials.Credentials")
    mocker.patch("app.api.Google_Calendar.google_calendar_.session", {"credentials": MagicMock()})
    oauth_mock.return_value = MagicMock()
    oauth_mock.expired == False
    oauth_mock.refresh_token == False

    service_mock = mocker.patch("app.api.Google_Calendar.google_calendar_.googleapiclient.discovery", return_value = MagicMock())
    service_mock.build.return_value.return_value.insert.return_value.execute.return_value = MagicMock()
    service_mock.events.insert.execute.get.return_value = "Testing Works"

    response = google_calendar_.create_calendar(task_list,date)
    assert response == general_utils.CalendarStatus.EMPTY

def test_calendar_fail_invalid_input_time(mocker):
    """Tasks with malformed time strings (e.g. "16:00s") fail time conversion and return EMPTY."""
    date = "2025-02-05"
    task_list = [{
        "time_begin": "16:00s",
        "time_end": "16:00aaa",
        "task_name": "Test",
        "description": "Testing description",
        "location": "Vancouver"
    }]
    oauth_mock = mocker.patch("app.api.Google_Calendar.google_calendar_.google.oauth2.credentials.Credentials")
    mocker.patch("app.api.Google_Calendar.google_calendar_.session", {"credentials": MagicMock()})
    oauth_mock.return_value = MagicMock()
    oauth_mock.expired == False
    oauth_mock.refresh_token == False

    service_mock = mocker.patch("app.api.Google_Calendar.google_calendar_.googleapiclient.discovery", return_value = MagicMock())
    service_mock.build.return_value.return_value.insert.return_value.execute.return_value = MagicMock()
    service_mock.events.insert.execute.get.return_value = "Testing Works"

    response = google_calendar_.create_calendar(task_list,date)
    assert response == general_utils.CalendarStatus.EMPTY

def test_calendar_fail_oauth_fail(mocker):
    """Credentials constructor returning None causes an AttributeError and returns EMPTY."""
    date = "2025-02-05"
    task_list = [{
        "time_begin": "16:00",
        "time_end": "16:00",
        "task_name": "Test",
        "description": "Testing description",
        "location": "Vancouver"
    }]
    oauth_mock = mocker.patch("app.api.Google_Calendar.google_calendar_.google.oauth2.credentials.Credentials")
    mocker.patch("app.api.Google_Calendar.google_calendar_.session", {"credentials": MagicMock()})
    oauth_mock.return_value = None

    service_mock = mocker.patch("app.api.Google_Calendar.google_calendar_.googleapiclient.discovery", return_value = MagicMock())
    service_mock.build.return_value.return_value.insert.return_value.execute.return_value = MagicMock()
    service_mock.events.insert.execute.get.return_value = "Testing Works"
    
    response = google_calendar_.create_calendar(task_list,date)
    assert response == general_utils.CalendarStatus.EMPTY

def test_calendar_fail_service_fail(mocker):
    """Google Calendar service raises an exception on execute and returns EMPTY."""
    date = "2025-02-05"
    task_list = [{
        "time_begin": "16:00",
        "time_end": "16:00",
        "task_name": "Test",
        "description": "Testing description",
        "location": "Vancouver"
    }]
    oauth_mock = mocker.patch("app.api.Google_Calendar.google_calendar_.google.oauth2.credentials.Credentials")
    mocker.patch("app.api.Google_Calendar.google_calendar_.session", {"credentials": MagicMock()})
    oauth_mock.return_value = MagicMock()
    oauth_mock.expired == False
    oauth_mock.refresh_token == False
    
    service_mock = mocker.patch("app.api.Google_Calendar.google_calendar_.googleapiclient.discovery")
    service_mock.build.return_value.events.return_value.insert.return_value.execute.return_value.get.side_effect = Exception("Failed")
    
    response = google_calendar_.create_calendar(task_list,date)
    assert response == general_utils.CalendarStatus.EMPTY
    