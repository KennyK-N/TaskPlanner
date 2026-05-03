from dotenv import load_dotenv
from flask import Flask
import os

load_dotenv(".env")

from . import app_config
from app.Main.views import app_route
from app.api import *
from app.auth import *
from app.database import *
from app.redis import *


def create_app():
    gemini = gemini_.gemini_init()

    app = Flask(__name__)
    app.config.from_object(app_config.APP_CONFIG)
    db.init_app(app)
    crud.init_table(app)

    app.extensions["gemini_CLIENT"] = gemini
    app.extensions["redis"] = redis_func.redis_init()

    app.register_blueprint(app_route)
    app.register_blueprint(api_bp)
    app.register_blueprint(auth)
    app.register_blueprint(db_bp)

    return app
