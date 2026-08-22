def menu():
    return {
        "ok": True,
        "actions": ["health", "create", "list", "get", "update", "delete"],
        "fields": ["workspace_id", "entry_type", "title", "body", "tags"],
    }
