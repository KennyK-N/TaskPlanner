import pytest
from unittest.mock import MagicMock
from flask import session

HOME = "/" 

def test_authorize_already_logged_in(mocker, client):
    """User already has credentials in session so they're redirected straight to home."""
    mocker.patch("app.util.permission_utils.check_view_access", return_value=True)
    res = client.get("/authorize")
    assert res.status_code == 302
    assert res.location == HOME
    


def test_authorize_starts_oauth_flow(mocker, client):
    """No credentials in session so the OAuth flow starts and redirects to Google."""
    mocker.patch("app.util.permission_utils.check_view_access", return_value=False)

    mock_flow = MagicMock()
    mock_flow.authorization_url.return_value = ("https://accounts.google.com/auth", "mock_state")
    mock_flow.code_verifier = "mock_verifier"

    mocker.patch(
        "google_auth_oauthlib.flow.Flow.from_client_config",
        return_value=mock_flow,
    )

    res = client.get("/authorize")
    assert res.status_code == 302
    assert res.location == "https://accounts.google.com/auth"


def test_oauth2callback_success(mocker, client):
    """Valid state and code in the callback populates the session and redirects to home."""
    mock_flow = MagicMock()
    mock_credentials = MagicMock()
    mock_credentials.refresh_token = "mock_refresh_token"
    mock_flow.credentials = mock_credentials

    mocker.patch(
        "google_auth_oauthlib.flow.Flow.from_client_config",
        return_value=mock_flow,
    )
    mocker.patch(
        "app.util.permission_utils.credentials_to_dict",
        return_value={
            "token": "mock_token",
            "refresh_token": "mock_refresh_token",
            "granted_scopes": ["email"],
        },
    )
    mocker.patch(
        "app.util.permission_utils.check_granted_scopes",
        return_value={"calendar": True},
    )

    with client.session_transaction() as sess:
        sess["state"] = "mock_state"
        sess["code_verifier"] = "mock_verifier"

    res = client.get("/oauth2callback?state=mock_state&code=mock_code")
    assert res.status_code == 302
    assert res.location == HOME


def test_oauth2callback_preserves_old_refresh_token(mocker, client):
    """New credentials have no refresh token so the old one from the session is kept."""
    mock_flow = MagicMock()
    mock_flow.credentials = MagicMock()

    mocker.patch(
        "google_auth_oauthlib.flow.Flow.from_client_config",
        return_value=mock_flow,
    )
    mocker.patch(
        "app.util.permission_utils.credentials_to_dict",
        return_value={"token": "new_token", "refresh_token": None},
    )
    mocker.patch(
        "app.util.permission_utils.check_granted_scopes",
        return_value={},
    )

    with client.session_transaction() as sess:
        sess["state"] = "mock_state"
        sess["code_verifier"] = "mock_verifier"
        sess["credentials"] = {"refresh_token": "old_refresh_token"}

    res = client.get("/oauth2callback?state=mock_state&code=mock_code")
    assert res.status_code == 302
    assert res.location == HOME

def test_oauth2callback_missing_state_fails(mocker, client):
    """Missing session state causes an exception which is caught and redirects to home."""
    mocker.patch(
        "google_auth_oauthlib.flow.Flow.from_client_config",
        side_effect=Exception("No state in session"),
    )

    res = client.get("/oauth2callback?code=mock_code")
    assert res.status_code == 302
    assert res.location == HOME

def test_oauth2callback_fetch_token_fails(mocker, client):
    """fetch_token raises an exception which is caught and redirects to home."""
    mock_flow = MagicMock()
    mock_flow.fetch_token.side_effect = Exception("Token fetch failed")

    mocker.patch(
        "google_auth_oauthlib.flow.Flow.from_client_config",
        return_value=mock_flow,
    )

    with client.session_transaction() as sess:
        sess["state"] = "mock_state"
        sess["code_verifier"] = "mock_verifier"

    res = client.get("/oauth2callback?state=mock_state&code=bad_code")
    assert res.status_code == 302
    assert res.location == HOME

def test_refresh_token_success(mocker, flask_app_mock):
    """Valid session credentials refresh successfully and profile_info is saved to session."""
    from app.auth.authentication import refresh_token

    mock_credentials_instance = MagicMock()
    mocker.patch(
        "google.oauth2.credentials.Credentials",
        return_value=mock_credentials_instance,
    )
    mocker.patch("google.auth.transport.requests.Request")
    mocker.patch(
        "app.util.permission_utils.credentials_to_dict",
        return_value={"token": "refreshed_token", "refresh_token": "rt"},
    )
    mocker.patch(
        "app.util.permission_utils.check_granted_scopes",
        return_value={"calendar": True},
    )

    mock_response = MagicMock()
    mock_response.text = '{"id": "123", "email": "test@test.com"}'
    mocker.patch("requests.get", return_value=mock_response)

    with flask_app_mock.test_request_context():
        session["credentials"] = {
            "token": "old_token",
            "refresh_token": "rt",
            "granted_scopes": ["email"],
        }
        refresh_token()
        assert session["profile_info"] == mock_response.text
    

def test_refresh_token_fails_gracefully(mocker, flask_app_mock):
    """Credentials constructor raises an exception which is caught silently without crashing."""
    from app.auth.authentication import refresh_token

    mocker.patch(
        "google.oauth2.credentials.Credentials",
        side_effect=Exception("Credentials error"),
    )

    with flask_app_mock.test_request_context():
        session["credentials"] = {
            "token": "old_token",
            "refresh_token": "rt",
            "granted_scopes": ["email"],
        }
        refresh_token() 


def test_refresh_token_missing_credentials(mocker, flask_app_mock):
    """Missing credentials key in session raises a KeyError which is caught silently."""
    from app.auth.authentication import refresh_token

    mocker.patch(
        "google.oauth2.credentials.Credentials",
        side_effect=KeyError("credentials"),
    )

    with flask_app_mock.test_request_context():
        session.clear()
        refresh_token()


def test_revoke_success(mocker, client):
    """Logged-in user successfully revokes their token, session is cleared, and redirects to home."""
    mocker.patch("app.util.permission_utils.check_view_access", return_value=True)

    mock_credentials_instance = MagicMock()
    mock_credentials_instance.token = "mock_token"
    mocker.patch(
        "google.oauth2.credentials.Credentials",
        return_value=mock_credentials_instance,
    )

    mock_revoke_response = MagicMock()
    mock_revoke_response.status_code = 200
    mocker.patch("requests.post", return_value=mock_revoke_response)

    with client.session_transaction() as sess:
        sess["credentials"] = {
            "token": "mock_token",
            "refresh_token": "rt",
            "granted_scopes": ["email"],
        }
        sess["features"] = {"calendar": True}
        sess["profile_info"] = '{"id": "123"}'

    res = client.get("/revoke")
    assert res.status_code == 302
    assert res.location == HOME

def test_revoke_not_logged_in(mocker, client):
    """User has no credentials so the exception is caught and redirects to home."""
    mocker.patch("app.util.permission_utils.check_view_access", return_value=False)

    res = client.get("/revoke")
    assert res.status_code == 302
    assert res.location == HOME

def test_revoke_post_request_fails(mocker, client):
    """requests.post raises a network error which is caught and redirects to home."""
    mocker.patch("app.util.permission_utils.check_view_access", return_value=True)

    mock_credentials_instance = MagicMock()
    mock_credentials_instance.token = "mock_token"
    mocker.patch(
        "google.oauth2.credentials.Credentials",
        return_value=mock_credentials_instance,
    )
    mocker.patch("requests.post", side_effect=Exception("Network error"))

    with client.session_transaction() as sess:
        sess["credentials"] = {
            "token": "mock_token",
            "refresh_token": "rt",
            "granted_scopes": ["email"],
        }
        sess["features"] = {}
        sess["profile_info"] = "{}"

    res = client.get("/revoke")
    assert res.status_code == 302
    assert res.location == HOME