from pydantic import BaseModel, field_validator
import datetime
from .general_utils import TIME_FORMAT


def validate_hhmm_format(value: str) -> str:
    """
    Checks if a string is a valid HH:MM time format.
    Args:
        value (str): The time string to validate e.g. "09:00".
    Returns:
        bool: True if valid HH:MM format, False otherwise.
    """
    try:
        _ = datetime.datetime.strptime(value, TIME_FORMAT)
        return True
    except Exception as exception:
        print(exception)
        return False


class Schedule_task(BaseModel):
    """Pydantic model for a single generated task"""

    task_name: str
    description: str
    time_begin: str
    time_end: str
    location: str

    """validates that time fields are in HH:MM format."""

    @field_validator("time_begin", "time_end")
    def validate_time_format(cls, time_val: str) -> str:
        is_HHMM_Format = validate_hhmm_format(time_val)
        if is_HHMM_Format == False:
            raise ValueError("Time must be in HH:MM format")
        return time_val
