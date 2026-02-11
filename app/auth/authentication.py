
from flask import request, session, redirect, url_for, flash
from google.auth.transport.requests import Request
import google.oauth2.credentials
import google_auth_oauthlib.flow
import requests

from .config import OAUTH_INFO
from . import auth
from app.util import *


@auth.route('/authorize', methods=['GET'])
def authorize():
  HasViewAccess = permission_utils.check_view_access()
  if HasViewAccess:
    return redirect(url_for("app_route.home"))
  
  flow = google_auth_oauthlib.flow.Flow.from_client_config(
      client_config=OAUTH_INFO["CLIENT_SECRETS_FILE"], scopes=OAUTH_INFO["SCOPES"])

  flow.redirect_uri = url_for('auth.oauth2callback', _external=True)

  authorization_url, state = flow.authorization_url(
      access_type='offline',
      include_granted_scopes='true')

  session['state'] = state

  return redirect(authorization_url)

@auth.route('/oauth2callback', methods=['GET'])
def oauth2callback():
  try:
    state = session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config=OAUTH_INFO["CLIENT_SECRETS_FILE"], scopes=OAUTH_INFO["SCOPES"], state=state)
    flow.redirect_uri = url_for('auth.oauth2callback', _external=True)

    authorization_response = request.url

    flow.fetch_token(authorization_response=authorization_response)
    
    credentials = flow.credentials

    credentials = permission_utils.credentials_to_dict(credentials)
    old_credentials = session.get('credentials', {})
    credentials['refresh_token'] = (
        credentials.get('refresh_token')
        if credentials.get('refresh_token') is not None
        else old_credentials.get('refresh_token')
    )

    session['credentials'] = credentials
    features = permission_utils.check_granted_scopes(credentials)
    session['features'] = features
    session["QUERY_RANGE"] = (0,5)
    return redirect(url_for("app_route.home"))
  except Exception as exception:
    print(exception)
    redirect_message = {'success': False, 'message': "Failed to login"}
    flash(redirect_message)
    return redirect(url_for("app_route.home"))

def refresh_token():
    try:
      client_config = OAUTH_INFO["CLIENT_SECRETS_FILE"]["web"]

      session_credentials = session['credentials']

      credentials = google.oauth2.credentials.Credentials(
          refresh_token=session_credentials.get('refresh_token'),
          scopes=session_credentials.get('granted_scopes'),
          token=session_credentials.get('token'),
          client_id=client_config.get('client_id'),
          client_secret=client_config.get('client_secret'),
          token_uri=client_config.get('token_uri')
      )

      credentials.refresh(Request())

      credentials = permission_utils.credentials_to_dict(credentials)
      
      session['credentials'] = credentials
      features = permission_utils.check_granted_scopes(credentials)
      session['features'] = features

      credentials = session['credentials']
      url = f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={credentials['token']}"
      profile_info = requests.get(url)
      session['profile_info'] = profile_info.text

    except Exception as exception:
      print(exception)

@auth.route('/revoke', methods=['GET'])
def revoke():
  HasViewAccess = permission_utils.check_view_access()
  try:
    if HasViewAccess == False:
        raise Exception
    
    client_config = OAUTH_INFO["CLIENT_SECRETS_FILE"]["web"]

    session_credentials = session['credentials']

    credentials = google.oauth2.credentials.Credentials(
        refresh_token=session_credentials.get('refresh_token'),
        scopes=session_credentials.get('granted_scopes'),
        token=session_credentials.get('token'),
        client_id=client_config.get('client_id'),
        client_secret=client_config.get('client_secret'),
        token_uri=client_config.get('token_uri'))

    revoke = requests.post('https://oauth2.googleapis.com/revoke',
        params={'token': credentials.token},
        headers = {'content-type': 'application/x-www-form-urlencoded'})

    status_code = getattr(revoke, 'status_code')
    del session['credentials']
    del session['features']
    del session['profile_info']
    redirect_message = {'success': True, 'message': "Successfully logged out"}
    flash(redirect_message)
      
    return redirect(url_for("app_route.home"))
  except Exception as exception:
      print(exception)
      redirect_message = {'success': False, 'message': "Failed to log out, User is not logged in"}
      flash(redirect_message)
      return redirect(url_for("app_route.home"))
