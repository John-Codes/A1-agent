import shlex
import subprocess

from config import SHELL_TIMEOUT, SHELL_WORKDIR

ALLOWED_COMMANDS = {
    "pwd",
    "ls",
    "find",
    "rg",
    "sed",
    "cat",
    "head",
    "tail",
    "wc",
    "python3",
}

BLOCKED_TOKENS = {
    ";",
    "&&",
    "||",
    "|",
    ">",
    "<",
    "`",
    "$(",
}


def run_shell(command):
    blocked = _blocked_reason(command)
    if blocked:
        return f"Blocked shell command: {blocked}"

    args = shlex.split(command)
    if not args:
        return "No shell command provided."
    if args[0] not in ALLOWED_COMMANDS:
        return f"Blocked shell command: {args[0]} is not allowed."
    if args[0] == "python3" and args[1:3] != ["-m", "py_compile"]:
        return "Blocked shell command: python3 is only allowed for -m py_compile."
    if args[0] == "find" and any(x in args for x in ["-delete", "-exec"]):
        return "Blocked shell command: unsafe find option."
    if args[0] == "sed" and "-i" in args:
        return "Blocked shell command: sed edits are not allowed."

    result = subprocess.run(
        args,
        cwd=SHELL_WORKDIR,
        text=True,
        capture_output=True,
        timeout=SHELL_TIMEOUT,
        check=False,
    )
    output = "\n".join(x for x in [result.stdout, result.stderr] if x).strip()
    return output[:4000] or f"Command exited with code {result.returncode}."


def _blocked_reason(command):
    for token in BLOCKED_TOKENS:
        if token in command:
            return f"contains {token}"
    return None
