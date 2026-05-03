from flask import request, jsonify
from . import db_bp
from app.util import *

from .crud import delete_task, retrieve_tasks


@db_bp.route("/retrieve", methods=["GET"])
def pagination_result():
    """
    Returns a paginated list of the user's schedules as JSON.
    Args:
        offset (int): Query param for the page offset e.g. /retrieve?offset=1.
    Returns:
        dict: Paginated task data and a status code.
    """
    offset = request.args.get("offset", type=int)
    query = retrieve_tasks(offset)
    return query


@db_bp.route("/delete", methods=["DELETE"])
def delete_cur_task():
    """
    Deletes a task by id and returns the result as JSON.
    Args:
        TaskId (int): Query param for the task to delete e.g. /delete?TaskId=1.
    Returns:
        Response: JSON with success (bool) and a message string.
    """
    task_id = request.args.get("TaskId", type=int)
    res = delete_task(task_id)
    return jsonify(res)
