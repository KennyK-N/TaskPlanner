import pytest
from app.util.general_utils import CREDENTIALS

def test_main_success(client, mocker):
    """Logged-in user with credentials in session gets the index page rendered with status 200."""
    with client.session_transaction() as sess:
        sess["profile_info"] = {}
        sess[CREDENTIALS] = {}
    mock_perm = mocker.patch("app.Main.views.permission_utils.check_view_access")
    mock_perm.return_value = True

    mock_get = mocker.patch("app.Main.views.requests.get")
    mock_get.status_code = 200
    mock_get.return_value = {}

    mock_crud_retrieve = mocker.patch("app.Main.views.crud.retrieve_tasks")
    mock_crud_retrieve.return_value = {
        "id": 1,
        "data": {},
        "name": "test"
        }
    
    mock_render = mocker.patch("app.Main.views.render_template")
    mock_render.return_value = ""

    response = client.get("/")
    assert response.status_code == 200
    assert b"" in response.data

def test_main_no_access(client, mocker):
    """User without view access gets the login page rendered with status 200."""
    with client.session_transaction() as sess:
        sess["profile_info"] = {}
        sess[CREDENTIALS] = {}

    mock_perm = mocker.patch("app.Main.views.permission_utils.check_view_access")
    mock_perm.return_value = False
    
    mock_render = mocker.patch("app.Main.views.render_template")
    mock_render.return_value = ""

    response = client.get("/")
    assert response.status_code == 200
    assert b"" in response.data