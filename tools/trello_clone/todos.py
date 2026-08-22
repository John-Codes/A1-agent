CREATE_FIELDS = {"title"}
UPDATE_FIELDS = {"title", "done"}


def add_todo(client, data):
    task_id = _required(data, "task_id")
    return client.post(f"/tasks/{task_id}/todos", _pick(data, CREATE_FIELDS))


def update_todo(client, data):
    task_id = _required(data, "task_id")
    todo_id = _required(data, "todo_id")
    return client.patch(f"/tasks/{task_id}/todos/{todo_id}", _pick(data, UPDATE_FIELDS))


def delete_todo(client, data):
    task_id = _required(data, "task_id")
    todo_id = _required(data, "todo_id")
    return client.delete(f"/tasks/{task_id}/todos/{todo_id}")


def _pick(data, fields):
    return {key: value for key, value in data.items() if key in fields and value is not None}


def _required(data, key):
    value = data.get(key)
    if not value:
        raise ValueError(f"Missing required field: {key}")
    return value
