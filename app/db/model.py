import json
from flask import jsonify, request, session
from sqlalchemy import Integer, text, TIMESTAMP, Numeric, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from . import db, db_bp
from app.util import *
from .config import TABLE_NAME, SUCCESS, ERROR, PAGE_SIZE

class Tasks(db.Model):
    __tablename__ = TABLE_NAME
    id = db.Column(Integer, primary_key=True)
    modified_at = db.Column(TIMESTAMP(timezone=True), default=func.now())
    data = db.Column(JSONB)
    oauth_id = db.Column(Numeric)
    name = db.Column(Text)
    
def init_table(app):
    with app.app_context():
        db.create_all()
        db.session.execute(text('ALTER TABLE Tasks ENABLE ROW LEVEL SECURITY;'))
        db.session.commit()

def insert_task(data, schedule_name):
    try:
        json_b_data = json.dumps(data)
        id = int(json.loads(session['profile_info'])["id"])
        data = Tasks(data = json_b_data, oauth_id = id, name = schedule_name)
        db.session.add(data)
        db.session.commit()
    except Exception as exception:
        print(exception)

def retrieve_tasks(offset):
    try:
        id = int(json.loads(session['profile_info'])["id"])    
        page = offset + 1
        query = db.paginate(db.select(Tasks).where(Tasks.oauth_id == id).order_by(Tasks.modified_at), page=page, per_page=PAGE_SIZE)
        
        items = []

        for item in query:
            tasks = json.loads(item.data) if type(item.data) == str else item.data
            item = {
                "id": item.id,
                "modified_at": item.modified_at,
                "name": item.name,
                "task": tasks
            }
            items.append(item)

        for record in items:
            date_time = record['modified_at']
            record['modified_at'] = time_conversion_utils.utc_to_local_timezone(date_time)

        return {
            "data": items,
            "status": SUCCESS
        }
    
    except Exception as exception:
        print(exception)
        return {"status" : ERROR}

def retrieve_single_item(task_id):
    try:
        user_id = int(json.loads(session['profile_info'])["id"])
        query = db.session.execute(db.select(Tasks).
                                   where((Tasks.id == task_id) & (Tasks.oauth_id == user_id))).scalars().first()
        data = json.loads(query.data)
        item = {
            "id": query.id,
            "data": data,
            "name": query.name
        }
        return item
    except Exception as exception:
        print(exception)
        return None

@db_bp.route('/retrieve', methods=["GET"])
def pagination_result():
    offset = request.args.get('offset', type=int)
    query = retrieve_tasks(offset)
    return query

@db_bp.route('/delete', methods=["DELETE"])
def delete_task():
    try:
        task_id = request.args.get('TaskId', type = int)

        if task_id == None:
            raise Exception
        
        user_id = int(json.loads(session['profile_info'])["id"])
            
        query = db.session.execute(db.select(Tasks).
                                   where((Tasks.id == task_id) & (Tasks.oauth_id == user_id))).scalars().first()

        db.session.delete(query)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": f"Successfully deleted task{task_id}"
        })
    except Exception as exception:
        print(exception)
