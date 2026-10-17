import fcntl
import time
from contextlib import contextmanager

from features.terminal_output.status import emit
from task_runtime.limits import ATTEMPTS, RUN_SECONDS, TASK_SECONDS
from task_runtime.state import PATH, load, next_task, save, status, validate_plan
from task_runtime.supervisor import EmergencyStop, supervise
from task_runtime.terminal import keyboard


@contextmanager
def exclusive():
    with PATH.with_suffix('.lock').open('w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError('Another terminal owns the task controller.') from None
        yield


def command(text):
    name, _, body = text.partition(' ')
    if name not in {'/plan', '/execute', '/resume', '/status'}:
        return None
    try:
        with exclusive():
            state = load()
            if name == '/status':
                return status(state)
            if name == '/plan':
                state['mode'] = 'plan'
                save(state)
                if body.strip():
                    with keyboard() as fd:
                        emit("PLAN", "Building plan. Esc stops immediately.", "cyan")
                        result = supervise('plan', {'goal': body.strip()}, fd)
                    tasks = validate_plan(result)
                    state.update(goal=body.strip(), tasks=tasks)
                    save(state)
            else:
                if not state['tasks']:
                    return 'Create a plan first: /plan <goal>'
                with keyboard() as fd:
                    execute(state, fd, resume=name == '/resume')
            return status(state)
    except EmergencyStop:
        from heartbeat.service import service
        service.stop()
        return 'STOPPED | Execution stopped. Inspect effects, then use /resume explicitly.'
    except (Exception, KeyboardInterrupt) as exc:
        return f'ERROR | {exc or "Interrupted"}'


def execute(state, fd, resume=False):
    state['mode'] = 'execute'
    if resume:
        for task in state['tasks']:
            if task['status'] in {'interrupted', 'blocked', 'failed'} and task['attempts'] < ATTEMPTS:
                task['status'] = 'pending'
    save(state)
    started = time.monotonic()
    while time.monotonic() - started < RUN_SECONDS:
        task = next_task(state)
        if task is None:
            break
        task.update(status='running', attempts=task['attempts'] + 1)
        save(state)
        emit("EXECUTE", f"{task['id']}: {task['title']} | Esc: EMERGENCY STOP", "cyan")
        try:
            result = supervise('execute', {'goal': state['goal'], 'task': task,
                               'tasks': state['tasks']}, fd,
                               timeout=min(TASK_SECONDS, RUN_SECONDS - (time.monotonic() - started)))
            outcome = result.get('status')
            evidence = result.get('evidence')
            if outcome not in {'done', 'blocked', 'failed'} or not isinstance(evidence, str) or not evidence.strip():
                raise ValueError('Worker must report a valid status and completion evidence.')
            task.update(status=outcome, detail=evidence)
        except (EmergencyStop, KeyboardInterrupt):
            task.update(status='interrupted', detail='Emergency stop; inspect effects before retrying.')
            state['mode'] = 'stopped'
            save(state)
            raise EmergencyStop() from None
        except Exception as exc:
            task.update(status='failed', detail=str(exc))
        save(state)
        emit(task['status'].upper(), f"{task['id']}: {task['detail']}", _tone(task['status']))
    state['mode'] = 'idle'
    save(state)
    if any(t['status'] != 'done' for t in state['tasks']):
        emit("PAUSED", f"Unfinished tasks remain; inspect /status. Attempt limit: {ATTEMPTS}.", "yellow")


def _tone(status):
    return {"done": "green", "failed": "red", "blocked": "yellow", "interrupted": "yellow"}.get(status, "cyan")
