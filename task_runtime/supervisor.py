import multiprocessing
import time

from task_runtime.processes import kill
from task_runtime.terminal import escaped
from task_runtime.worker import run


class EmergencyStop(Exception):
    pass


def supervise(mode, payload, fd, emit=print, timeout=600, target=run, cancel=None):
    if (cancel is not None and cancel.is_set()) or (fd is not None and escaped(fd)):
        raise EmergencyStop("Emergency stop requested")
    from store import store
    payload = dict(payload, _runtime={k: v for k, v in store.items()
                                     if k.startswith("active_")})
    context = multiprocessing.get_context("spawn")
    reader, writer = context.Pipe(duplex=False)
    process = context.Process(target=target, args=(writer, mode, payload))
    process.start()
    writer.close()
    grouped = False
    started = time.monotonic()
    try:
        while True:
            if (cancel is not None and cancel.is_set()) or (fd is not None and escaped(fd)):
                raise EmergencyStop("Emergency stop requested")
            if time.monotonic() - started > timeout:
                raise TimeoutError("Worker runtime limit reached")
            if reader.poll(0.05):
                try:
                    kind, value = reader.recv()
                except EOFError:
                    raise RuntimeError("Worker exited without a result") from None
                if kind == "ready":
                    grouped = True
                elif kind == "event":
                    emit(f"ACTIVITY | {value}", flush=True)
                elif kind == "result":
                    return value
                elif kind == "error":
                    raise RuntimeError(value)
            elif not process.is_alive():
                raise RuntimeError("Worker exited without a result")
    except KeyboardInterrupt:
        raise EmergencyStop("Ctrl-C emergency stop requested") from None
    finally:
        # Also clean up descendants after success; no detached work is retained.
        kill(process.pid, grouped)
        process.join(2)
        reader.close()
        process.close()
