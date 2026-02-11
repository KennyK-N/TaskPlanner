import os 

class APP_CONFIG:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
    DEBUG = bool(os.getenv("DEBUG"))

    SQLALCHEMY_DATABASE_URI = os.getenv("POSTGRES_URI_STRING")
    SQLALCHEMY_TRACK_MODIFICATIONS = False