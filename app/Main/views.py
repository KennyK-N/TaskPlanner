from flask import (
    Blueprint,
    render_template,
    jsonify,
    request,
    current_app,
    session,
    redirect,
    url_for,
)
from app.util import *
import requests
from app.db import model

app_route = Blueprint("app_route", __name__, template_folder="templates")


@app_route.app_errorhandler(404)
def page_not_found(error):
    return redirect("/")


@app_route.route("/", methods=["GET"])
def home():
    HasViewAccess = permission_utils.check_view_access()
    if HasViewAccess:
        Start_Offset = 0
        credentials = session["credentials"]

        if "profile_info" not in session:
            url = f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={credentials['token']}"
            profile_info = requests.get(url)
            session["profile_info"] = profile_info.text

        query = model.retrieve_tasks(Start_Offset)
        data = query["data"]

        return render_template("index.html", data=data)
    else:
        return render_template("login.html")
