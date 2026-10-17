import os
import sys
import termios

from features.terminal_output import input_prompt
from features.terminal_output.status import status_line
from task_runtime.terminal import keyboard


def read_input(service):
    if not sys.stdin.isatty():
        return input(input_prompt())
    sys.stdout.write(input_prompt())
    sys.stdout.flush()
    text = bytearray()
    with keyboard() as fd:
        while True:
            char = os.read(fd, 1)
            if not char or char == b'\x04':
                print()
                return '/quit'
            if char == b'\x1b':
                termios.tcflush(fd, termios.TCIFLUSH)
                service.stop()
                print()
                print(status_line("STOPPED", "Heartbeat paused. /heartbeat resume to restart.", "red"))
                return ''
            if char in (b'\r', b'\n'):
                print()
                return text.decode('utf-8', errors='replace')
            if char in (b'\x7f', b'\x08'):
                if text:
                    decoded = text.decode('utf-8', errors='replace')[:-1]
                    text = bytearray(decoded.encode())
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()
            elif char >= b' ':
                text.extend(char)
                os.write(sys.stdout.fileno(), char)
