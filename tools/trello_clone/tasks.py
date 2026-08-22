FIELDS = {"board_id", "title", "description", "status", "priority", "order", "due_at"}
UPDATE_FIELDS = {"title", "description", "status", "priority", "order", "due_at"}


def create_task(client, data):
    return client.post("/tasks", _pick(data, FIELDS))


def list_tasks(client, data):
    return client.get("/tasks", _params(data, {"board_id", "limit", "skip"}))


def get_task(client, data):
    return client.get(f"/tasks/{_required(data, 'task_id')}")


def update_task(client, data):
    task_id = _required(data, "task_id")
    return client.patch(f"/tasks/{task_id}", _pick(data, UPDATE_FIELDS))


def delete_task(client, data):
    return client.delete(f"/tasks/{_required(data, 'task_id')}")


def _pick(data, fields):
    return {key: value for key, value in data.items() if key in fields and value is not None}


def _params(data, fields):
    return _pick(data, fields) or None


def _required(data, key):
    value = data.get(key)
    if not value:
        raise ValueError(f"Missing required field: {key}")
    return value
