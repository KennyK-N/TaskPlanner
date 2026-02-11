from flask import session

from .general_utils import FEATURES, CREDENTIALS


def check_granted_scopes(credentials):
    features = {}
    if "https://www.googleapis.com/auth/calendar" in credentials["granted_scopes"]:
        features["calendar"] = True
    else:
        features["calendar"] = False

    return features


def credentials_to_dict(credentials):
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "granted_scopes": credentials.granted_scopes,
    }


def check_calendar_access():
    from app.auth.authentication import refresh_token

    if FEATURES not in session:
        return False

    features = session[FEATURES]
    if features["calendar"] == False:
        return False

    return True


def check_view_access():
    if CREDENTIALS in session:
        return True
    else:
        return False
