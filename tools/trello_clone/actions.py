import json

from tools.trello_clone.boards import create_board, delete_board, get_board, list_boards, update_board
from tools.trello_clone.client import TrelloCloneClient, dumps
from tools.trello_clone.menu import menu
from tools.trello_clone.projects import (
    create_project,
    delete_project,
    get_project,
    list_projects,
    update_project,
)
from tools.trello_clone.tasks import create_task, delete_task, get_task, list_tasks, update_task
from tools.trello_clone.todos import add_todo, delete_todo, update_todo

ACTIONS = {
    "ping": lambda client, data: client.get("/ping"),
    "health": lambda client, data: client.get("/health"),
    "create_project": create_project,
    "list_projects": list_projects,
    "get_project": get_project,
    "update_project": update_project,
    "delete_project": delete_project,
    "create_board": create_board,
    "list_boards": list_boards,
    "get_board": get_board,
    "update_board": update_board,
    "delete_board": delete_board,
    "create_task": create_task,
    "list_tasks": list_tasks,
    "get_task": get_task,
    "update_task": update_task,
    "delete_task": delete_task,
    "add_todo": add_todo,
    "update_todo": update_todo,
    "delete_todo": delete_todo,
}


def run_trello_clone(body):
    data = _load(body)
    action = data.pop("action", "menu").strip()
    if action == "menu":
        return menu()
    handler = ACTIONS.get(action)
    if not handler:
        raise ValueError(f"Unknown Trello Clone action: {action}")
    return dumps(handler(TrelloCloneClient(), data))


def _load(body):
    if not body.strip():
        return {"action": "menu"}
    try:
        data = json.loads(body)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Trello Clone body must be JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Trello Clone body must be a JSON object")
    return data
