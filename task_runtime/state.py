import json
import os
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / ".a1-tasks.json"


def load(path=PATH):
    if not path.exists():
        return {"mode": "plan", "goal": "", "tasks": []}
    state = json.loads(path.read_text())
    for task in state["tasks"]:
        if task["status"] == "running":
            task["status"] = "interrupted"
            task["detail"] = "Previous run ended; inspect effects before resuming."
    return state


def save(state, path=PATH):
    temporary = path.with_suffix(".tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        os.chmod(temporary, 0o600)
        json.dump(state, stream, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def validate_plan(data):
    tasks = data.get("tasks")
    if not isinstance(tasks, list) or not 1 <= len(tasks) <= 50:
        raise ValueError("Plan must contain 1–50 tasks.")
    seen = set()
    for task in tasks:
        identifier = task.get("id")
        if not isinstance(identifier, str) or not identifier or identifier in seen:
            raise ValueError("Task IDs must be unique strings.")
        if not all(isinstance(task.get(k), str) and task[k].strip()
                   for k in ("title", "instructions", "check")):
            raise ValueError("Each task needs a title, instructions, and completion check.")
        deps = task.get("depends_on", [])
        if not isinstance(deps, list) or any(d not in seen for d in deps):
            raise ValueError("Dependencies must refer to earlier tasks.")
        task.update(depends_on=deps, status="pending", attempts=0, detail="")
        seen.add(identifier)
    return tasks


def next_task(state):
    done = {t["id"] for t in state["tasks"] if t["status"] == "done"}
    return next((t for t in state["tasks"] if t["status"] == "pending"
                 and set(t["depends_on"]) <= done), None)


def status(state):
    rows = [f"Mode: {state['mode']} | Goal: {state['goal'] or '(none)'}"]
    rows += [f"{t['id']} [{t['status']}] {t['title']} — {t['detail']}\n"
             f"  Do: {t['instructions']}\n  Check: {t['check']} | Depends on: {t['depends_on']}"
             for t in state["tasks"]]
    return "\n".join(rows)
