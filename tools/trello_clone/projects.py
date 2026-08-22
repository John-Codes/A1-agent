FIELDS = {"name", "description"}


def create_project(client, data):
    return client.post("/projects", _pick(data, FIELDS))


def list_projects(client, data):
    return client.get("/projects", _params(data, {"limit", "skip"}))


def get_project(client, data):
    return client.get(f"/projects/{_required(data, 'project_id')}")


def update_project(client, data):
    project_id = _required(data, "project_id")
    return client.patch(f"/projects/{project_id}", _pick(data, FIELDS))


def delete_project(client, data):
    return client.delete(f"/projects/{_required(data, 'project_id')}")


def _pick(data, fields):
    return {key: value for key, value in data.items() if key in fields and value is not None}


def _params(data, fields):
    return _pick(data, fields) or None


def _required(data, key):
    value = data.get(key)
    if not value:
        raise ValueError(f"Missing required field: {key}")
    return value
