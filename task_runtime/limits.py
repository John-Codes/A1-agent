import os


def positive(name, default):
    value = int(os.environ.get(name, default))
    if value <= 0:
        raise ValueError(f'{name} must be positive')
    return value


TOOL_ROUNDS = positive('A1_TASK_TOOL_ROUNDS', 12)
TASK_SECONDS = positive('A1_TASK_TIMEOUT', 600)
RUN_SECONDS = positive('A1_RUN_TIMEOUT', 1800)
ATTEMPTS = positive('A1_TASK_ATTEMPTS', 3)
