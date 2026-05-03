from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

db_bp = Blueprint("db", __name__)

from . import crud, views

__all__ = ["db_bp", "crud", "db", "views"]
