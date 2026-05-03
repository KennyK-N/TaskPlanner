import pytest
from app.database.model import Tasks
from unittest.mock import MagicMock
from flask import Flask

from app.Main.views import app_route
from app.api import api_bp
from app.auth import auth
from app.database import db_bp
from app.database import db


@pytest.fixture
def flask_app_mock():
    """
    Creates a minimal Flask app wired up with all blueprints and mocked Redis/Gemini extensions for testing.
    """
    flask_app_mock = Flask(__name__)
    flask_app_mock.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "postgresql://postgres:postgres@localhost:5432/dummy_db",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "SECRET_KEY": "Test",
        }
    )

    db.init_app(flask_app_mock)
    flask_app_mock.extensions["gemini_CLIENT"] = MagicMock()
    flask_app_mock.extensions["redis"] = MagicMock()
    flask_app_mock.register_blueprint(app_route)
    flask_app_mock.register_blueprint(api_bp)
    flask_app_mock.register_blueprint(auth)
    flask_app_mock.register_blueprint(db_bp)

    yield flask_app_mock


@pytest.fixture()
def client(flask_app_mock):
    """Returns a Flask test client for making HTTP requests in tests."""
    return flask_app_mock.test_client()


@pytest.fixture
def mock_task_object():
    """Returns a dummy Tasks model instance with hardcoded test values."""
    task = Tasks(
        id=1,
        data={},
        oauth_id=123,
        name="Text",
        modified_at="2025-12-31 03:28:53.854222+00",
    )
    return task


@pytest.fixture
def mock_db_session(mocker):
    """Patches the SQLAlchemy db.session"""
    return mocker.patch("app.database.crud.db.session")


@pytest.fixture
def mock_db_profile_id(mocker):
    """Patches the Flask session in crud to return a fake user profile"""
    return mocker.patch("app.database.crud.session", {"profile_info": '{"id": 123}'})


@pytest.fixture
def mock_geocoding_profile_id(mocker):
    """Patches the Flask session in geocoding"""
    return mocker.patch(
        "app.api.Geocoding.geocoding_.session", {"profile_info": '{"id": 123}'}
    )


@pytest.fixture
def mock_db_redis_set(mocker):
    """Patches redis_set in crud."""
    return mocker.patch("app.database.crud.redis_set")


@pytest.fixture
def mock_db_redis_get(mocker):
    """
    Returns an instance that patches redis_get in crud with a configurable return value.
    """

    def _mock_db_redis_get(val):
        return mocker.patch("app.database.crud.redis_get", return_value=val)

    return _mock_db_redis_get


@pytest.fixture
def mock_geocoding_redis_get(mocker):
    """
    Returns an instance that patches redis_get in geocoding with a configurable return value.
    """

    def _mock_geocoding_redis_get(val):
        return mocker.patch("app.api.Geocoding.geocoding_.redis_get", return_value=val)

    return _mock_geocoding_redis_get
