import pytest
from app.util import *
from app.redis.redis_func import *

def test_redis_get_success(mocker, flask_app_mock):
    """Redis returns a value for the given key."""
    flask_app_mock.extensions["redis"].get.return_value = "1" 
    with flask_app_mock.app_context():
        res = redis_get(1)
        assert res == "1"

def test_redis_set_success(mocker, flask_app_mock):
    """redis.set is called with the correct key, value, TTL, and nx flag."""
    redis_mock = flask_app_mock.extensions["redis"]
    with flask_app_mock.app_context():
        redis_set("key","value")
        redis_mock.set.assert_called_once_with(
            "key",
            "value",
            ex=REDIS_TTL_VAL,
            nx=True
        )

def test_redis_invalidate_success(mocker, flask_app_mock):
    """Deletes the direct key and then scans and deletes all matching paginate keys for the user."""
    redis_mock = flask_app_mock.extensions["redis"]
    with flask_app_mock.app_context():
        redis_invalidate("key","user")
        redis_mock.delete.assert_called_once_with(
            "key",
        )
        redis_mock.scan.assert_called_once()

def test_redis_get_fail(mocker, flask_app_mock):
    """Redis returns None for a missing key."""
    flask_app_mock.extensions["redis"].get.return_value = None 
    with flask_app_mock.app_context():
        res = redis_get(1)
        assert res == None

def test_redis_set_fail(mocker, flask_app_mock, capfd):
    """Redis raises an exception on set and the error message is printed to stdout."""
    redis_mock = flask_app_mock.extensions["redis"]
    redis_mock.set.side_effect = Exception("Redis is down")

    with flask_app_mock.app_context():
        redis_set("my_key", "my_value")

        out, _ = capfd.readouterr()
        assert "Redis is down" in out

def test_redis_invalidate_fail(mocker, flask_app_mock, capfd):
    """Redis raises an exception on delete and the error message is printed to stdout."""
    redis_mock = flask_app_mock.extensions["redis"]
    redis_mock.delete.side_effect = Exception("Redis is down")

    with flask_app_mock.app_context():
        redis_invalidate("key","user")
        redis_mock.delete.assert_called_once_with(
            "key",
        )
        out, _ = capfd.readouterr()
        assert "Redis is down" in out