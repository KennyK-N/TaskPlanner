import json
from flask import session
from sqlalchemy import text
from . import db
from app.util import *
from .config import SUCCESS, ERROR, PAGE_SIZE
from .model import Tasks
from app.redis.redis_func import *

def init_table(app):
    """
    Creates all database tables and enables row level security on the Tasks table.
    Args:
        app (Flask): The Flask app instance used to push an app context.
    Returns:
        None
    """
    with app.app_context():
        db.create_all()
        db.session.execute(text("ALTER TABLE Tasks ENABLE ROW LEVEL SECURITY;"))
        db.session.commit()

def insert_task(data, schedule_name):
    """
    Saves a new task schedule to the database and caches it in Redis.
    Args:
        data (dict): The task list data to serialize and store.
        schedule_name (str): The display name for this schedule.
    Returns:
        None
    """
    try:
        json_b_data = json.dumps(data)
        user_id = int(json.loads(session["profile_info"])["id"])
        task = Tasks(data=json_b_data, oauth_id=user_id, name=schedule_name)
        db.session.add(task)
        db.session.commit()
        key = f"{user_id}{general_utils.REDIS_RECORD_KEY_FORMAT}{task.id}"
        task_value = {
            "id": task.id,
            "data": data,
            "name": task.name
        }
        redis_invalidate(key, user_id)
        redis_set(key, json.dumps(task_value))
    except Exception as exception:
        print("Error:", exception)

def retrieve_tasks(offset):
    """
    Fetches a paginated list of the user's schedules from Redis or the database.
    Args:
        offset (int): The page offset used to calculate which page to fetch.
    Returns:
        dict: Contains a data list of task records and a status code.
    """
    try:
        user_id = int(json.loads(session["profile_info"])["id"])
        page = offset + 1
        key = f"{user_id}{general_utils.REDIS_PAGINATE_KEY_FORMAT}{offset}"
        cached = redis_get(key)

        if cached != None:
            return json.loads(cached)
        
        query = db.paginate(
            db.select(Tasks).where(Tasks.oauth_id == user_id).order_by(Tasks.modified_at),
            page=page,
            per_page=PAGE_SIZE,
        )

        items = []

        for item in query:
            tasks = json.loads(item.data) if type(item.data) == str else item.data
            item = {
                "id": item.id,
                "modified_at": item.modified_at,
                "name": item.name,
                "task": tasks,
            }
            items.append(item)

        for record in items:
            date_time = record["modified_at"]
            record["modified_at"] = time_conversion_utils.utc_to_local_timezone(
                date_time
            )

        output = {"data": items, "status": SUCCESS}
        redis_set(key, json.dumps(output))

        return output

    except Exception as exception:
        print("Error:", exception)
        return {"status": ERROR}

def retrieve_single_item(task_id):
    """
    Fetches a single task by id from Redis or the database.
    Args:
        task_id (int): The id of the task to retrieve.
    Returns:
        dict | None: The task as a dict, or None if not found or an error occurs.
    """
    try:
        user_id = int(json.loads(session["profile_info"])["id"])
        key = f"{user_id}{general_utils.REDIS_RECORD_KEY_FORMAT}{task_id}"
        cached = redis_get(key)
        if cached:
            return json.loads(cached)
        
        query = (
            db.session.execute(
                db.select(Tasks).where(
                    (Tasks.id == task_id) & (Tasks.oauth_id == user_id)
                )
            )
            .scalars()
            .first()
        )
        data = json.loads(query.data)
        item = {"id": query.id, "data": data, "name": query.name}
        redis_set(key, json.dumps(item))
        return item
    except Exception as exception:
        print("Error:", exception)
        return None

def delete_task(task_id):
    """
    Deletes a task from the database and invalidates its Redis cache entries.
    Args:
        task_id (int): The id of the task to delete.
    Returns:
        dict: Contains success (bool) and a message string.
    """
    try:
        if task_id == None:
            raise Exception

        user_id = int(json.loads(session["profile_info"])["id"])
        key = f"{user_id}{general_utils.REDIS_RECORD_KEY_FORMAT}{task_id}"
    
        query = (
            db.session.execute(
                db.select(Tasks).where(
                    (Tasks.id == task_id) & (Tasks.oauth_id == user_id)
                )
            )
            .scalars()
            .first()
        )

        db.session.delete(query)
        db.session.commit()
        redis_invalidate(key, user_id)
        return {"success": True, "message": f"Successfully deleted task{task_id}"}

    except Exception as exception:
        print("Error:", exception)
        return {"success": False, "message": f"Failed to deleted task{task_id}"}

