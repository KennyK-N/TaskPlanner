from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

db_bp = Blueprint("db", __name__)

from . import model

__all__ = ["db_bp", "model", "db"]
