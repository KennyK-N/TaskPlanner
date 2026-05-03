import pytest
import app.database.crud as crud_module
from unittest.mock import MagicMock
import json
from app.database.config import ERROR
from types import SimpleNamespace

def test_retrieve_single_item_success(mocker, mock_db_session, mock_db_profile_id, mock_db_redis_set, mock_db_redis_get):
    """Fetches a task from the DB by id and returns it as a parsed dict."""
    mock_obj = SimpleNamespace(
        id=1,
        name ="Test",
        data=json.dumps({"test": "works"})
    )

    mock_db_redis_get(None)
    mock_db_session.execute.return_value.scalars.return_value.first.return_value = mock_obj

    res = crud_module.retrieve_single_item(1)
    
    assert res["data"] == {"test": "works"}

def test_retrieve_single_item_redis_success(mocker, mock_db_session, mock_db_profile_id, mock_db_redis_set, mock_db_redis_get):
    """Returns a cached task from Redis without hitting the database."""
    mock_obj = {
        "id": 1,
        "name": "Test",
        "data": {"test": "works"}
    }

    mock_db_redis_get(json.dumps(mock_obj))

    res = crud_module.retrieve_single_item(1)
    assert res["data"] == {"test": "works"}

def test_insert_success(
                mocker, 
                mock_task_object, 
                mock_db_session, 
                mock_db_profile_id, mock_db_redis_set):
    """Valid data and schedule name causes db.session.add and commit to be called once each."""
    data = mock_task_object.as_dict()
    schedule_name = "test"
    
    crud_module.insert_task(data, schedule_name)
    
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()

def test_retrieve_tasks_success(mocker, mock_db_profile_id, mock_task_object, mock_db_redis_set, mock_db_redis_get):
    """Paginates tasks from the DB and returns a dict with data and status 200."""
    mocker.patch("app.database.crud.db.paginate", return_value=[mock_task_object]);

    mock_db_redis_get(None)

    res = crud_module.retrieve_tasks(1)

    assert (res["data"][0]["name"], res["status"]) == ("Text", 200)

def test_retrieve_tasks_redis_success(mocker, mock_db_profile_id, mock_task_object, mock_db_redis_set, mock_db_redis_get):
    """Returns paginated results from Redis cache without touching the database."""
    mock_db_redis_get(json.dumps({"data": [mock_task_object.as_dict()], "status":200}))

    res = crud_module.retrieve_tasks(1)

    assert (res["data"][0]["name"], res["status"]) == ("Text", 200)

def test_delete_task_success(mocker, mock_task_object, mock_db_profile_id, mock_db_session):
    """Finds the task and calls db.session.delete and commit, returning success True."""
    mock_db_session.execute.return_value.scalars.return_value.first.return_value = mock_task_object

    mocker.patch("app.database.crud.redis_invalidate")

    res = crud_module.delete_task(1)

    mock_db_session.delete.assert_called_once()
    mock_db_session.commit.assert_called_once()
    assert res["success"] == True

def test_retrieve_single_item_fail(mocker, mock_db_session, mock_db_profile_id):
    """Query returns a MagicMock instead of a real object so json.loads fails and returns None."""
    mock_obj = MagicMock()

    mock_db_session.execute.return_value.scalars.return_value.first.return_value = mock_obj

    res = crud_module.retrieve_single_item(1)
    assert res == None

def test_insert_fail(
                mocker, 
                mock_task_object, 
                mock_db_session, 
                mock_db_profile_id):
    """Passing a Tasks object instead of a dict causes json.dumps to fail so add and commit are never called."""
    data = mock_task_object 
    schedule_name = "test"

    crud_module.insert_task(data, schedule_name)

    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_not_called()

def test_profile_id_fail(mocker):
    """No session profile_info causes a KeyError and returns status ERROR."""
    res = crud_module.retrieve_tasks(1)

    assert res["status"] == ERROR

def test_delete_task_fail(mocker, mock_task_object, mock_db_profile_id, mock_db_session):
    """db.session.delete raises an exception so commit is never called and success is False."""
    mock_db_session.execute.return_value.scalars.return_value.first.return_value = None
    mock_db_session.delete.side_effect = Exception("Failed to delete")

    res = crud_module.delete_task(1)

    mock_db_session.delete.assert_called_once()
    mock_db_session.commit.assert_not_called()
    assert res["success"] == False