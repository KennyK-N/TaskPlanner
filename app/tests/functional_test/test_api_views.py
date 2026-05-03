import pytest
from app.util.general_utils import CalendarStatus

def test_prompt_success(mocker, client):
    """User has view and calendar access so the prompt page renders with 200."""
    mocker.patch("app.api.views.permission_utils.check_view_access", return_value = True)
    mocker.patch("app.api.views.permission_utils.check_calendar_access", return_value = True)
    mocker.patch("app.api.views.render_template")

    response = client.get("/prompt")

    assert response.status_code == 200

def test_fail_prompt_HasViewAccess_fail(mocker, client):
    """No view access flashes an error and redirects with 302."""
    mocker.patch("app.api.views.permission_utils.check_view_access", return_value = False)
    response = client.get("/prompt")

    with client.session_transaction() as session:
        flashes = session.get('_flashes')
        assert flashes is not None

    assert response.status_code == 302

def test_fail_prompt_HasCalendarAccess_fail(mocker, client):
    """No calendar access flashes an error and redirects with 302."""
    mocker.patch("app.api.views.permission_utils.check_view_access", return_value = True)
    mocker.patch("app.api.views.permission_utils.check_calendar_access", return_value = False)
    response = client.get("/prompt")
    
    with client.session_transaction() as session:
        flashes = session.get('_flashes')
        assert flashes is not None

    assert response.status_code == 302


def test_task_finalize_no_view_access(mocker, client):
    """No view access on POST flashes an error and redirects with 302."""
    mocker.patch("app.api.views.permission_utils.check_view_access", return_value=False)
    response = client.post("/task_finalize")

    with client.session_transaction() as sess:
        assert sess.get("_flashes") is not None

    assert response.status_code == 302

def test_task_finalize_no_calendar_access(mocker, client):
    """No calendar access on POST flashes an error and redirects with 302."""
    mocker.patch("app.api.views.permission_utils.check_view_access", return_value=True)
    mocker.patch("app.api.views.permission_utils.check_calendar_access", return_value=False)
    response = client.post("/task_finalize")

    with client.session_transaction() as sess:
        assert sess.get("_flashes") is not None

    assert response.status_code == 302

def test_task_finalize_get_redirects_to_prompt(mocker, client):
    """GET request to task_finalize always redirects back to the prompt page."""
    mocker.patch("app.api.views.permission_utils.check_view_access", return_value=True)
    mocker.patch("app.api.views.permission_utils.check_calendar_access", return_value=True)

    response = client.get("/task_finalize")

    assert response.status_code == 302

def test_task_finalize_invalid_input_empty_task_list(mocker, client):
    """Empty task input flashes an invalid input error and redirects with 302."""
    mocker.patch("app.api.views.permission_utils.check_view_access", return_value=True)
    mocker.patch("app.api.views.permission_utils.check_calendar_access", return_value=True)
    mocker.patch("app.api.views.sanitize_utils.clean_value", return_value="")

    response = client.post("/task_finalize", data={
        "itemsInput": "",
        "date": "2025-01-01",
        "schedule_name": "Test"
    })

    with client.session_transaction() as sess:
        assert sess.get("_flashes") is not None

    assert response.status_code == 302

def test_task_finalize_invalid_input_too_many_tasks(mocker, client):
    """More than 5 tasks flashes an invalid input error and redirects with 302."""
    mocker.patch("app.api.views.permission_utils.check_view_access", return_value=True)
    mocker.patch("app.api.views.permission_utils.check_calendar_access", return_value=True)
    mocker.patch("app.api.views.sanitize_utils.clean_value", return_value="a, b, c, d, e, f")

    response = client.post("/task_finalize", data={
        "itemsInput": "a, b, c, d, e, f",
        "date": "2025-01-01",
        "schedule_name": "Test"
    })

    with client.session_transaction() as sess:
        assert sess.get("_flashes") is not None

    assert response.status_code == 302

def test_task_finalize_gemini_returns_none(mocker, client):
    """Gemini returning None flashes an invalid output error and redirects with 302."""
    mocker.patch("app.api.views.permission_utils.check_view_access", return_value=True)
    mocker.patch("app.api.views.permission_utils.check_calendar_access", return_value=True)
    mocker.patch("app.api.views.sanitize_utils.clean_value", return_value="task1, task2")
    mocker.patch("app.api.views.geocoding_.get_addr", return_value=None)
    mocker.patch("app.api.views.gemini_.generate_tasks", return_value=None)

    response = client.post("/task_finalize", data={
        "itemsInput": "task1, task2",
        "date": "2025-01-01",
        "schedule_name": "Test"
    })

    with client.session_transaction() as sess:
        assert sess.get("_flashes") is not None

    assert response.status_code == 302

def test_task_finalize_success(mocker, client):
    """Valid input with location generates tasks and renders the finalize template with 200."""
    mocker.patch("app.api.views.permission_utils.check_view_access", return_value=True)
    mocker.patch("app.api.views.permission_utils.check_calendar_access", return_value=True)
    mocker.patch("app.api.views.sanitize_utils.clean_value", return_value="task1, task2")
    mocker.patch("app.api.views.geocoding_.get_addr", return_value="123 Test St")
    mocker.patch("app.api.views.gemini_.generate_tasks", return_value=[{"task_name": "task1"}])
    mocker.patch("app.api.views.render_template", return_value="rendered")

    response = client.post("/task_finalize", data={
        "itemsInput": "task1, task2",
        "date": "2025-01-01",
        "schedule_name": "Test",
        "location": "on"
    })

    assert response.status_code == 200


def test_create_event_no_view_access(mocker, client):
    """No view access on POST flashes an error and redirects with 302."""
    mocker.patch("app.api.views.permission_utils.check_view_access", return_value=False)
    response = client.post("/create_event")

    with client.session_transaction() as sess:
        assert sess.get("_flashes") is not None

    assert response.status_code == 302

def test_create_event_no_calendar_access(mocker, client):
    """No calendar access on POST flashes an error and redirects with 302."""
    mocker.patch("app.api.views.permission_utils.check_view_access", return_value=True)
    mocker.patch("app.api.views.permission_utils.check_calendar_access", return_value=False)
    response = client.post("/create_event")

    with client.session_transaction() as sess:
        assert sess.get("_flashes") is not None

    assert response.status_code == 302

def test_create_event_get_request_redirects(mocker, client):
    """GET request to create_event flashes an error and redirects with 302."""
    mocker.patch("app.api.views.permission_utils.check_view_access", return_value=True)
    mocker.patch("app.api.views.permission_utils.check_calendar_access", return_value=True)
    response = client.get("/create_event")

    with client.session_transaction() as sess:
        assert sess.get("_flashes") is not None

    assert response.status_code == 302

def test_create_event_invalid_input_missing_date(mocker, client):
    """Missing date field flashes an invalid input error and redirects with 302."""
    mocker.patch("app.api.views.permission_utils.check_view_access", return_value=True)
    mocker.patch("app.api.views.permission_utils.check_calendar_access", return_value=True)
    mocker.patch("app.api.views.sanitize_utils.clean_value", return_value=["t",])
    mocker.patch("app.api.views.sanitize_utils.clean_list", return_value=["task1",])

    response = client.post("/create_event", data={
        "task_name": "task1",
        "description": "desc",
        "time_begin": "09:00",
        "time_end": "10:00",
        "location": "None",
        "schedule_for": "",
        "schedule_name": "Test"
    })

    with client.session_transaction() as sess:
        assert sess.get("_flashes") is not None

    assert response.status_code == 302

def test_create_event_time_violation(mocker, client):
    """End time before start time flashes a time error and redirects with 302."""
    mocker.patch("app.api.views.permission_utils.check_view_access", return_value=True)
    mocker.patch("app.api.views.permission_utils.check_calendar_access", return_value=True)
    mocker.patch("app.api.views.sanitize_utils.clean_value", side_effect=["2025-01-01", "Test"])
    mocker.patch("app.api.views.sanitize_utils.clean_list", side_effect=[
        ["task1"], ["desc"], ["10:00"], ["09:00"], ["None"]
    ])
    mocker.patch("app.api.views.task_util.task_violate_time_check", return_value=True)

    response = client.post("/create_event", data={
        "task_name": "task1",
        "description": "desc",
        "time_begin": "10:00",
        "time_end": "09:00",
        "location": "None",
        "schedule_for": "2025-01-01",
        "schedule_name": "Test"
    })

    with client.session_transaction() as sess:
        assert sess.get("_flashes") is not None

    assert response.status_code == 302

def test_create_event_calendar_revoke(mocker, client):
    """Calendar returns REVOKE status so permissions error is flashed and redirects with 302."""
    mocker.patch("app.api.views.permission_utils.check_view_access", return_value=True)
    mocker.patch("app.api.views.permission_utils.check_calendar_access", return_value=True)
    mocker.patch("app.api.views.sanitize_utils.clean_value", side_effect=["2025-01-01", "Test"])
    mocker.patch("app.api.views.sanitize_utils.clean_list", side_effect=[
        ["task1"], ["desc"], ["09:00"], ["10:00"], ["None"]
    ])
    mocker.patch("app.api.views.task_util.task_violate_time_check", return_value=False)
    mocker.patch("app.api.views.task_util.create_task_list", return_value=[])
    mocker.patch("app.api.views.refresh_token")
    mocker.patch("app.api.views.google_calendar_.create_calendar", return_value=CalendarStatus.REVOKE)

    response = client.post("/create_event", data={
        "task_name": "task1",
        "description": "desc",
        "time_begin": "09:00",
        "time_end": "10:00",
        "location": "None",
        "schedule_for": "2025-01-01",
        "schedule_name": "Test"
    })

    with client.session_transaction() as sess:
        assert sess.get("_flashes") is not None

    assert response.status_code == 302

def test_create_event_calendar_empty(mocker, client):
    """Calendar returns EMPTY status so failure message is flashed and redirects with 302."""
    mocker.patch("app.api.views.permission_utils.check_view_access", return_value=True)
    mocker.patch("app.api.views.permission_utils.check_calendar_access", return_value=True)
    mocker.patch("app.api.views.sanitize_utils.clean_value", side_effect=["2025-01-01", "Test"])
    mocker.patch("app.api.views.sanitize_utils.clean_list", side_effect=[
        ["task1"], ["desc"], ["09:00"], ["10:00"], ["None"]
    ])
    mocker.patch("app.api.views.task_util.task_violate_time_check", return_value=False)
    mocker.patch("app.api.views.task_util.create_task_list", return_value=[])
    mocker.patch("app.api.views.refresh_token")
    mocker.patch("app.api.views.google_calendar_.create_calendar", return_value=CalendarStatus.EMPTY)

    response = client.post("/create_event", data={
        "task_name": "task1",
        "description": "desc",
        "time_begin": "09:00",
        "time_end": "10:00",
        "location": "None",
        "schedule_for": "2025-01-01",
        "schedule_name": "Test"
    })

    with client.session_transaction() as sess:
        assert sess.get("_flashes") is not None

    assert response.status_code == 302

def test_create_event_success(mocker, client):
    """Valid event is created, task is inserted to DB, success is flashed and redirects with 302."""
    mocker.patch("app.api.views.permission_utils.check_view_access", return_value=True)
    mocker.patch("app.api.views.permission_utils.check_calendar_access", return_value=True)
    mocker.patch("app.api.views.sanitize_utils.clean_value", side_effect=["2025-01-01", "Test"])
    mocker.patch("app.api.views.sanitize_utils.clean_list", side_effect=[
        ["task1"], ["desc"], ["09:00"], ["10:00"], ["None"]
    ])
    mocker.patch("app.api.views.task_util.task_violate_time_check", return_value=False)
    mocker.patch("app.api.views.task_util.create_task_list", return_value=[])
    mocker.patch("app.api.views.refresh_token")
    mocker.patch("app.api.views.google_calendar_.create_calendar", return_value=CalendarStatus.SUCCESS)
    mocker.patch("app.api.views.db_services.insert_task")

    response = client.post("/create_event", data={
        "task_name": "task1",
        "description": "desc",
        "time_begin": "09:00",
        "time_end": "10:00",
        "location": "None",
        "schedule_for": "2025-01-01",
        "schedule_name": "Test"
    })

    with client.session_transaction() as sess:
        assert sess.get("_flashes") is not None

    assert response.status_code == 302


def test_create_schedule_no_view_access(mocker, client):
    """No view access flashes an error and redirects with 302."""
    mocker.patch("app.api.views.permission_utils.check_view_access", return_value=False)
    response = client.post("/create_google_schedule")

    with client.session_transaction() as sess:
        assert sess.get("_flashes") is not None

    assert response.status_code == 302

def test_create_schedule_no_calendar_access(mocker, client):
    """No calendar access flashes an error and redirects with 302."""
    mocker.patch("app.api.views.permission_utils.check_view_access", return_value=True)
    mocker.patch("app.api.views.permission_utils.check_calendar_access", return_value=False)
    response = client.post("/create_google_schedule")

    with client.session_transaction() as sess:
        assert sess.get("_flashes") is not None

    assert response.status_code == 302

def test_create_schedule_invalid_task(mocker, client):
    """retrieve_single_item returns None so the response JSON has success False."""
    mocker.patch("app.api.views.permission_utils.check_view_access", return_value=True)
    mocker.patch("app.api.views.permission_utils.check_calendar_access", return_value=True)
    mocker.patch("app.api.views.db_services.retrieve_single_item", return_value=None)

    response = client.post("/create_google_schedule?TaskId=99&date=2025-01-01")
    data = response.get_json()

    assert data["success"] == False
    assert response.status_code == 200

def test_create_schedule_calendar_revoke(mocker, client):
    """Calendar returns REVOKE so the response JSON has success False."""
    mocker.patch("app.api.views.permission_utils.check_view_access", return_value=True)
    mocker.patch("app.api.views.permission_utils.check_calendar_access", return_value=True)
    mocker.patch("app.api.views.db_services.retrieve_single_item", return_value={"data": [], "name": "Test"})
    mocker.patch("app.api.views.google_calendar_.create_calendar", return_value=CalendarStatus.REVOKE)

    response = client.post("/create_google_schedule?TaskId=1&date=2025-01-01")
    data = response.get_json()

    assert data["success"] == False

def test_create_schedule_calendar_empty(mocker, client):
    """Calendar returns EMPTY so the response JSON has success False."""
    mocker.patch("app.api.views.permission_utils.check_view_access", return_value=True)
    mocker.patch("app.api.views.permission_utils.check_calendar_access", return_value=True)
    mocker.patch("app.api.views.db_services.retrieve_single_item", return_value={"data": [], "name": "Test"})
    mocker.patch("app.api.views.google_calendar_.create_calendar", return_value=CalendarStatus.EMPTY)

    response = client.post("/create_google_schedule?TaskId=1&date=2025-01-01")
    data = response.get_json()

    assert data["success"] == False

def test_create_schedule_success(mocker, client):
    """Calendar creates events successfully so the response JSON has success True."""
    mocker.patch("app.api.views.permission_utils.check_view_access", return_value=True)
    mocker.patch("app.api.views.permission_utils.check_calendar_access", return_value=True)
    mocker.patch("app.api.views.db_services.retrieve_single_item", return_value={"data": [], "name": "Test"})
    mocker.patch("app.api.views.google_calendar_.create_calendar", return_value=CalendarStatus.SUCCESS)

    response = client.post("/create_google_schedule?TaskId=1&date=2025-01-01")
    data = response.get_json()
    
    assert data["success"] == True