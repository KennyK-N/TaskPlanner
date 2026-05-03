from flask import session

from .general_utils import FEATURES, CREDENTIALS


def check_granted_scopes(credentials):
    """
    Checks which Google API scopes the user has been granted and returns a feature flag dict.
    Args:
        credentials (dict): The user's OAuth credentials containing granted_scopes.
    Returns:
        dict: e.g. {"calendar": True} or {"calendar": False}.
    """
    features = {}
    if "https://www.googleapis.com/auth/calendar" in credentials["granted_scopes"]:
        features["calendar"] = True
    else:
        features["calendar"] = False

    return features


def credentials_to_dict(credentials):
    """
    Converts a Google OAuth credentials object into a plain dict for session storage.
    Args:
        credentials (google.oauth2.credentials.Credentials): The credentials object.
    Returns:
        dict: Contains token, refresh_token, and granted_scopes.
    """
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "granted_scopes": credentials.granted_scopes,
    }


def check_calendar_access():
    """
    Checks if the current session user has been granted Google Calendar access.
    Returns:
        bool: True if calendar access is granted, False otherwise.
    """
    from app.auth.authentication import refresh_token

    if FEATURES not in session:
        return False

    features = session[FEATURES]
    if features["calendar"] == False:
        return False

    return True


def check_view_access():
    """
    Checks if the user is logged in by looking for credentials in the session.
    Returns:
        bool: True if credentials exist in the session, False otherwise.
    """
    if CREDENTIALS in session:
        return True
    else:
        return False
