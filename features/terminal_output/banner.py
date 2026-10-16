import io
import json
import shutil

from rich import box
from rich.console import Console, Group
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from features.terminal_output.colors import color_enabled

ACCENTS = ("bright_cyan", "bright_magenta", "bright_green")
COMMANDS = (
    ("/markdown demo", "color preview"),
    ("/tools", "tool list"),
    ("/search <query>", "web search"),
    ("/history", "conversation"),
    ("/memory", "saved memory"),
    ("/log", "gateway log"),
    ("/tick", "heartbeat now"),
    ("/life_log <entry>", "private log"),
    ("/plan <goal>", "task loop"),
    ("/execute", "run the plan"),
    ("/status", "task status"),
    ("/seo help", "daily drafts"),
    ("/quit", "leave"),
)


def startup(names, seo_help, enabled=None):
    enabled = color_enabled() if enabled is None else enabled
    if not enabled:
        return _plain_startup(names, seo_help)
    body = Group(
        _section("Commands", _command_table()),
        Text(""),
        _section("Tools", _tool_table(names)),
        Text(""),
        _section("SEO", _seo_text(seo_help)),
        Text("Esc pauses the heartbeat", style="dim"),
    )
    panel = Panel(
        body,
        title="[bold bright_cyan]A1[/]",
        subtitle="[dim]type a message[/]",
        border_style="bright_cyan",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    return _capture(panel)


def tools_panel(names, enabled=None):
    enabled = color_enabled() if enabled is None else enabled
    names = list(names)
    if not enabled:
        return "\n".join(names)
    panel = Panel(
        _tool_table(names),
        title="[bold bright_magenta]Tools[/]",
        subtitle=f"[dim]{len(names)}[/]",
        border_style="magenta",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    return _capture(panel)


def tool_block(name, text, enabled):
    text = str(text or "")
    if not enabled:
        return None
    title = name or "DATA"
    panel = Panel(
        _tool_body(text),
        title=f"[bold bright_magenta]{title}[/]",
        border_style="magenta",
        box=box.ROUNDED,
        padding=(0, 1),
    )
    return _capture(panel)


def _plain_startup(names, seo_help):
    tools = ", ".join(names)
    return "\n".join([
        "Personal AI Gateway",
        "Type a message, /life_log <entry>, /history, /tools, /search <query>, /tick, /memory, /log, /markdown, or /quit.",
        "Tasks: /plan <goal>, /execute, /status, /resume. Esc stops active task work.",
        f"Tools: {tools}",
        str(seo_help or "").rstrip(),
    ])


def _section(title, body):
    return Group(Text(title, style="bold"), body)


def _command_table():
    table = Table.grid(padding=(0, 2))
    table.add_column(no_wrap=True)
    table.add_column()
    for command, hint in COMMANDS:
        table.add_row(Text(command, style="bold bright_cyan"), Text(hint, style="dim"))
    return table


def _tool_table(names):
    table = Table.grid(padding=(0, 2))
    for _ in range(3):
        table.add_column(no_wrap=True)
    row = []
    for index, name in enumerate(names):
        row.append(Text(str(name), style=ACCENTS[index % len(ACCENTS)]))
        if len(row) == 3:
            table.add_row(*row)
            row = []
    if row:
        table.add_row(*row)
    return table


def _seo_text(help_text):
    text = Text()
    for line in str(help_text or "").splitlines():
        command, hint = _split_help(line)
        if command:
            text.append(command, style="bold bright_green")
            if hint:
                text.append("  " + hint, style="dim")
        else:
            text.append(line, style="dim")
        text.append("\n")
    return text


def _split_help(line):
    stripped = line.strip()
    if not stripped.startswith("/"):
        return "", ""
    parts = line.split(None, 1)
    command = parts[0]
    rest = parts[1].strip() if len(parts) > 1 else ""
    if "  " in line:
        left, right = line.split("  ", 1)
        if left.strip().startswith("/"):
            return left.strip(), right.strip()
    return command, rest


def _tool_body(text):
    stripped = text.strip()
    if stripped[:1] in "{[":
        try:
            pretty = json.dumps(json.loads(stripped), indent=2)
        except json.JSONDecodeError:
            pretty = None
        if pretty is not None:
            return Syntax(pretty, "json", theme="ansi_dark", background_color="default")
    return Text(text)


def _capture(renderable):
    output = io.StringIO()
    width = max(40, min(100, shutil.get_terminal_size((80, 24)).columns))
    console = Console(
        file=output,
        force_terminal=True,
        color_system="standard",
        no_color=False,
        width=width,
        highlight=False,
    )
    console.print(renderable)
    return output.getvalue().rstrip()
