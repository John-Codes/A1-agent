import threading

import pytest

from task_runtime.supervisor import EmergencyStop, supervise
from tests.test_task_runtime import stalled_worker


def test_background_worker_cancel_needs_no_keyboard():
    cancel = threading.Event()
    def emit(*args, **kwargs):
        cancel.set()
    with pytest.raises(EmergencyStop):
        supervise('heartbeat', {}, None, emit=emit, target=stalled_worker, cancel=cancel)
