FIELDS = {"project_id", "name", "description"}
UPDATE_FIELDS = {"name", "description"}


def create_board(client, data):
    return client.post("/boards", _pick(data, FIELDS))


def list_boards(client, data):
    return client.get("/boards", _params(data, {"project_id", "limit", "skip"}))


def get_board(client, data):
    return client.get(f"/boards/{_required(data, 'board_id')}")


def update_board(client, data):
    board_id = _required(data, "board_id")
    return client.patch(f"/boards/{board_id}", _pick(data, UPDATE_FIELDS))


def delete_board(client, data):
    return client.delete(f"/boards/{_required(data, 'board_id')}")


def _pick(data, fields):
    return {key: value for key, value in data.items() if key in fields and value is not None}


def _params(data, fields):
    return _pick(data, fields) or None


def _required(data, key):
    value = data.get(key)
    if not value:
        raise ValueError(f"Missing required field: {key}")
    return value
