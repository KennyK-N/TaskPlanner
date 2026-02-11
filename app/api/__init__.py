from flask import Blueprint


api = Blueprint("api", __name__)

from . import views
from .Gemini import gemini_
from .Geocoding import geocoding_
from .Google_Calendar import google_calendar_

__all__ = ["api", "gemini_", "views", "geocoding_", "google_calendar_"]
