import fcntl
import threading
import time

from heartbeat import settings
from heartbeat.worker import run
from heartbeat import report
from task_runtime.supervisor import EmergencyStop, supervise


class Heartbeat:
    def __init__(self):
        self.closed = threading.Event()
        self.cancel = threading.Event()
        self.wake = threading.Event()
        self.busy = threading.Lock()
        self.thread = None
        self.paused = not settings.ENABLED
        self.last = {'status': 'idle', 'model': settings.MODEL}

    def start(self):
        if self.thread is None or not self.thread.is_alive():
            self.closed.clear()
            self.thread = threading.Thread(target=self._loop, daemon=True)
            self.thread.start()

    def _loop(self):
        deadline = time.monotonic() + settings.INTERVAL
        while not self.closed.is_set():
            manual = self.wake.wait(max(0, deadline - time.monotonic()))
            self.wake.clear()
            deadline = time.monotonic() + settings.INTERVAL
            if not self.closed.is_set() and not self.paused:
                self.tick(scheduled=not manual)

    def request(self):
        if self.busy.locked():
            return 'Heartbeat already running.'
        if self.paused:
            return 'Heartbeat paused. Use /heartbeat resume.'
        self.wake.set()
        return 'Heartbeat check requested in background.'

    def stop(self):
        self.paused = True
        self.cancel.set()

    def resume(self):
        if self.busy.locked():
            return 'Heartbeat is still stopping; try again shortly.'
        self.cancel.clear()
        self.paused = False
        return f'Heartbeat resumed; next check within {settings.INTERVAL} seconds.'

    def close(self):
        self.stop()
        self.closed.set()
        self.wake.set()
        if self.thread:
            self.thread.join(3)

    def tick(self, scheduled=False):
        if not self.busy.acquire(blocking=False):
            return {'response': 'Heartbeat already running.', 'error': None}
        try:
            try:
                from seo_mail import poll
                mail_result = poll()
                if mail_result.get('processed'):
                    print(f"SEO MAIL | processed {mail_result['processed']} reviewer message(s)", flush=True)
            except Exception as exc:
                print(f"SEO MAIL | error: {exc}", flush=True)
            if self.paused:
                return {'response': 'Heartbeat paused. Use /heartbeat resume.', 'error': None}
            with settings.PATH.with_suffix('.lock').open('w') as lock:
                try:
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError:
                    return {'response': 'Heartbeat running in another process.', 'error': None}
                if scheduled and not report.due():
                    return {'response': 'Heartbeat not due yet.', 'error': None}
                self.last = report.record('running')
                print(f'HEARTBEAT | Checking with {settings.PROVIDER}/{settings.MODEL}', flush=True)
                try:
                    result = supervise('heartbeat', {}, None, timeout=settings.TIMEOUT,
                                       target=run, cancel=self.cancel)
                    self.last = report.record('done', result.get('response', ''))
                    print(f"HEARTBEAT | {self.last['detail']}", flush=True)
                    return result
                except (Exception, EmergencyStop) as exc:
                    stopped = isinstance(exc, EmergencyStop)
                    self.last = report.record('stopped' if stopped else 'error', str(exc))
                    print(f"HEARTBEAT | {self.last['status']}: {self.last['detail']}", flush=True)
                    return {'response': '', 'error': self.last['detail']}
        finally:
            self.busy.release()

    def status(self):
        return report.status(self.paused)


service = Heartbeat()
