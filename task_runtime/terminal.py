import os
import select
import sys
import termios
import tty
from contextlib import contextmanager


@contextmanager
def keyboard():
    if not sys.stdin.isatty():
        raise RuntimeError("Execution requires an interactive terminal for emergency stop.")
    fd = sys.stdin.fileno()
    previous = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        yield fd
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, previous)


def escaped(fd):
    if not select.select([fd], [], [], 0)[0]:
        return False
    data = os.read(fd, 64)
    # Fail closed: any escape byte, including an arrow key, stops execution.
    return b"\x1b" in data or not data
