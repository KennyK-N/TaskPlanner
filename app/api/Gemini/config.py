from app.util import *

GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_CONFIG = {
    "temperature": 0.7,
    "response_mime_type": "application/json",
    "response_schema": list[prompt_schema.Schedule_task],
}
