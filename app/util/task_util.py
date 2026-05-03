def create_task_list(task_names, descriptions, time_begins, time_end, locations):
    """
    Zips parallel lists of task fields into a list of task dicts, setting missing values to None.
    Args:
        task_names (list[str]): List of task names.
        descriptions (list[str]): List of task descriptions.
        time_begins (list[str]): List of start times in HH:MM format.
        time_end (list[str]): List of end times in HH:MM format.
        locations (list[str]): List of locations.
    Returns:
        list[dict]: List of task dicts with keys task_name, description, time_begin, time_end, location.
    """
    tasks = []
    for i in range(len(task_names)):
        tasks.append(
            {
                "task_name": task_names[i] if task_names[i] else None,
                "description": descriptions[i] if descriptions[i] else None,
                "time_begin": time_begins[i] if time_begins[i] else None,
                "time_end": time_end[i] if time_end[i] else None,
                "location": locations[i] if locations[i] else None,
            }
        )
    return tasks


def task_violate_time_check(time_begins, time_end):
    """
    Checks if any task has an end time that is not after its start time.
    Args:
        time_begins (list[str]): List of start times in HH:MM format.
        time_end (list[str]): List of end times in HH:MM format.
    Returns:
        bool: True if any time violation is found, False if all times are valid.
    """
    try:
        for i in range(len(time_begins)):
            if time_end[i] <= time_begins[i]:
                return True
        return False
    except Exception as exception:
        print(exception)
        return True
