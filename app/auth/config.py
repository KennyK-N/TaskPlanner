import os

host = os.getenv("HOST")
port = os.getenv("PORT")
application_layer_protocol = os.getenv("APPLICATION_LAYER_PROTCOL")

CLIENT_ID = os.getenv("CLIENT_ID")
PROJECT_ID = os.getenv("PROJECT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URLS = [f"{application_layer_protocol}://{host}:{port}/oauth2callback"]
JAVASCRIPT_ORIGINS = [f"{application_layer_protocol}://{host}:{port}"]

OAUTH_INFO = {
    "SCOPES" : [
            'https://www.googleapis.com/auth/calendar',
            'email',
            'profile', 
            'openid'],

    "API_SERVICE_NAME" : 'calendar',

    "API_VERSION" : 'v3',

    "CLIENT_SECRETS_FILE" : {
        "web": {
            "client_id": CLIENT_ID,
               "project_id": PROJECT_ID,
               "auth_uri": "https://accounts.google.com/o/oauth2/auth",
               "token_uri": "https://oauth2.googleapis.com/token",
               "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
               "client_secret": CLIENT_SECRET,
               "redirect_uris": REDIRECT_URLS,
                "javascript_origins": JAVASCRIPT_ORIGINS
        }
    }
}