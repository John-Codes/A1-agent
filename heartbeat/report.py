import json
from datetime import datetime, timezone

from heartbeat import settings
from task_runtime.state import save


def read():
    return json.loads(settings.PATH.read_text()) if settings.PATH.exists() else {'status': 'idle'}


def record(status, detail=''):
    from tools.log import redact
    previous = read()
    value = {'status': status, 'model': settings.MODEL,
             'time': datetime.now(timezone.utc).isoformat(), 'detail': redact(detail)}
    value['started'] = value['time'] if status == 'running' else previous.get('started', value['time'])
    save(value, settings.PATH)
    return value


def due():
    stamp = read().get('started')
    return not stamp or (datetime.now(timezone.utc) - datetime.fromisoformat(stamp)).total_seconds() >= settings.INTERVAL


def status(paused):
    saved = read()
    return (f"Heartbeat: {'paused' if paused else 'scheduled'} every {settings.INTERVAL}s | "
            f"{settings.PROVIDER}/{settings.MODEL} | last: {saved.get('status')} "
            f"{saved.get('time', '')}\n{saved.get('detail', '')}")
