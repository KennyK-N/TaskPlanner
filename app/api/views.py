from .Google_Calendar import google_calendar_
from .Geocoding import geocoding_
from .Gemini import gemini_
from flask import render_template, jsonify, request, redirect, url_for, flash
from . import api
from app.auth.authentication import refresh_token
from app.util import *
from app.db import model as db_services

MAX_TASK_LIST_SIZE = 5

@api.route('/prompt', methods=['GET'])
def prompt():
    HasViewAccess = permission_utils.check_view_access()
    HasCalendarAccess = permission_utils.check_calendar_access()

    if HasViewAccess == False:
        redirect_message = {'success': False, 'message': "Login Credential is invalid"}
        flash(redirect_message)
        return redirect(url_for("app_route.home"))
    
    if HasCalendarAccess == False:
        redirect_message = {'success': False, 'message': "Calendar access not granted"}
        flash(redirect_message)
        return redirect(url_for("app_route.home"))
    
    return render_template('prompt.html')
   

@api.route("/task_finalize", methods=['POST', 'GET'])
def task_finalize():
    HasViewAccess = permission_utils.check_view_access()
    HasCalendarAccess = permission_utils.check_calendar_access()

    if HasViewAccess == False:
        redirect_message = {'success': False, 'message': "Login Credential is invalid"}
        flash(redirect_message)
        return redirect(url_for("app_route.home"))
    
    if HasCalendarAccess == False:
        redirect_message = {'success': False, 'message': "Calendar access not granted"}
        flash(redirect_message)
        return redirect(url_for("app_route.home"))
        
    if(request.method == 'POST'):
        task_list = (request.values.get("itemsInput") 
            if request.values.get("itemsInput") != None else None)
        
        clean = sanitize_utils.clean_value(task_list)

        task_list = [
            task.strip()
            for task in clean.split(",")
            if task.strip() != ""
        ]
        
        task_list_sz = len(task_list)
        
        date = request.values.get("date")
        schedule_name = request.values.get("schedule_name")
        location = "None"

        if request.values.get("location") is not None:
            location = geocoding_.get_addr()

        if (task_list_sz > MAX_TASK_LIST_SIZE or task_list_sz == 0) or (not task_list or not date or not schedule_name):
            redirect_message = {'success': False, 'message': "Invalid Input"}
            flash(redirect_message)
            return redirect(url_for("api.prompt"))
        

        generated_response = gemini_.generate_tasks(task_list, location)
        
        if generated_response == None:
            redirect_message = {'success': False, 'message': "Invalid Output"}
            flash(redirect_message)
            return redirect(url_for("api.prompt"))

        return render_template("task_finalize.html", Generated_Tasks = generated_response, schedule_for = date, schedule_name = schedule_name)
            
    return redirect(url_for("api.prompt"))


@api.route("/create_event", methods=['POST', 'GET'])
def create_event():
    HasViewAccess = permission_utils.check_view_access()
    HasCalendarAccess = permission_utils.check_calendar_access()

    if HasViewAccess == False:
        redirect_message = {'success': False, 'message': "Login Credential is invalid"}
        flash(redirect_message)
        return redirect(url_for("app_route.home"))
    
    if HasCalendarAccess == False:
        redirect_message = {'success': False, 'message': "Calendar access not granted"}
        flash(redirect_message)
        return redirect(url_for("app_route.home"))
    
    if(request.method == 'POST'):
        task_names = sanitize_utils.clean_list(request.values.getlist('task_name'))
        descriptions = sanitize_utils.clean_list(request.values.getlist('description'))
        time_begins = sanitize_utils.clean_list(request.values.getlist('time_begin'))
        time_end = sanitize_utils.clean_list(request.values.getlist('time_end'))
        locations = sanitize_utils.clean_list(request.values.getlist('location'))
        date = sanitize_utils.clean_value(request.values.get("schedule_for"))
        schedule_name = sanitize_utils.clean_value(request.values.get("schedule_name"))


        if not date or not schedule_name or len(time_begins) != len(time_end) or not task_names:
            redirect_message = {'success': False, 'message': "Invalid Input"}
            flash(redirect_message)
            return redirect('/')
        
        isViolatedTime = task_util.task_violate_time_check(time_begins=time_begins, time_end=time_end)
        
        if isViolatedTime:
            redirect_message = {'success': False, 'message': "End time must be after start time"}
            flash(redirect_message)
            return redirect('/')

        refresh_token()

        task_list = task_util.create_task_list(                
                task_names = task_names, 
                descriptions = descriptions,
                time_begins = time_begins,
                time_end = time_end,
                locations = locations)

        status = google_calendar_.create_calendar(
            task_list = task_list,
            date = date
        ) 

        if status is general_utils.CalendarStatus.REVOKE:
            redirect_message = {'success': False, 'message': "Invalid Permissions"}
            flash(redirect_message)
            return redirect(url_for("auth.revoke"))
        
        elif status is general_utils.CalendarStatus.EMPTY:
            redirect_message = {'success': False, 'message': "Failed to create schedule"}
            flash(redirect_message)
            return redirect(url_for("api.prompt")) 
        
        db_services.insert_task (task_list, schedule_name)
        redirect_message = {'success': True, 'message': "Successfully created task"}
        flash(redirect_message)
        return redirect(url_for("api.prompt")) 
    
    redirect_message = {'success': False, 'message': "Get Requests not allowed"}
    flash(redirect_message)
    return redirect(url_for("api.prompt"))

@api.route("/create_google_schedule", methods=['POST'])
def create_schedule():
    HasViewAccess = permission_utils.check_view_access()
    HasCalendarAccess = permission_utils.check_calendar_access()

    if HasViewAccess == False:
        redirect_message = {'success': False, 'message': "Login Credential is invalid"}
        flash(redirect_message)
        return redirect(url_for("app_route.home"))
    
    if HasCalendarAccess == False:
        redirect_message = {'success': False, 'message': "Calendar access not granted"}
        flash(redirect_message)
        return redirect(url_for("app_route.home"))

    task_id = request.args.get('TaskId', type = int)
    date = request.args.get("date")

    task = db_services.retrieve_single_item(task_id)
    if task == None:
        return jsonify({
            "success": False,
            "error": "Invalid task"
        })
    
    data = task["data"] 

    status = google_calendar_.create_calendar(
        task_list = data,
        date = date
    ) 

    if status is general_utils.CalendarStatus.REVOKE:
        return jsonify({
            "success": False,
            "message": "Invalid Permissions"
        }),
    
    if status is general_utils.CalendarStatus.EMPTY:
        return jsonify({
        "success": False,
        "error": "Failed to create due to empty calendar"
    })

    return jsonify({
        "success": True,
        "message": "Successfully created a calendar for current task"
    })
