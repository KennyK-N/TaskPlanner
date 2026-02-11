def create_task_list(task_names, descriptions, 
                    time_begins, time_end, 
                    locations):
    tasks = []
    for i in range(len(task_names)):
        tasks.append({
            'task_name': task_names[i] if task_names[i] else None,
            'description': descriptions[i] if descriptions[i] else None,
            'time_begin': time_begins[i] if time_begins[i] else None,
            'time_end': time_end[i] if time_end[i] else None,
            'location': locations[i] if locations[i] else None,
        })
    return tasks

def task_violate_time_check(time_begins, time_end):
    try:
        for i in range(len(time_begins)):
            if time_end[i] <= time_begins[i]:
                return True
        return False
    except Exception as exception:
        print(exception)
        return True