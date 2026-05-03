import pytest


def test_pagination_result_success(mocker, client, flask_app_mock):
    """GET /retrieve returns paginated tasks as JSON with status 200."""
    mocker.patch("app.database.views.retrieve_tasks", return_value={"test": "works"})
    res = client.get("/retrieve?offset=1")

    assert res.status_code == 200
    assert res.json == {"test": "works"}


def test_pagination_delete_success(mocker, client, flask_app_mock):
    """DELETE /delete calls delete_task and returns the result as JSON with status 200."""
    mocker.patch("app.database.views.delete_task", return_value={"test": "works"})
    response = client.delete("/delete?offset=1")
    assert response.status_code == 200
    assert response.json == {"test": "works"}
