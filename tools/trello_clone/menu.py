MENU = """Trello Clone smart task management tools

Health:
- ping
- health

Projects:
- create_project: name, description?
- list_projects: limit?, skip?
- get_project: project_id
- update_project: project_id, name?, description?
- delete_project: project_id

Boards:
- create_board: project_id, name, description?
- list_boards: project_id?, limit?, skip?
- get_board: board_id
- update_board: board_id, name?, description?
- delete_board: board_id

Tasks:
- create_task: board_id, title, description?, status?, priority?, order?, due_at?
- list_tasks: board_id?, limit?, skip?
- get_task: task_id
- update_task: task_id, title?, description?, status?, priority?, order?, due_at?
- delete_task: task_id

Todos:
- add_todo: task_id, title
- update_todo: task_id, todo_id, title?, done?
- delete_todo: task_id, todo_id
"""


def menu():
    return MENU
