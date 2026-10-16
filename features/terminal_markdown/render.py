"""Render model Markdown without changing stored responses or API payloads."""
import io
import os
import re
import shutil

from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text
from rich.theme import Theme

THEME = Theme({
    "markdown.h1": "bold bright_cyan",
    "markdown.h1.border": "bright_cyan",
    "markdown.h2": "bold cyan",
    "markdown.h3": "bold green",
    "markdown.h4": "bold blue",
    "markdown.h5": "blue",
    "markdown.h6": "dim blue",
    "markdown.strong": "bold",
    "markdown.em": "italic bright_magenta",
    "markdown.emph": "italic bright_magenta",
    "markdown.s": "dim strike",
    "markdown.code": "bold yellow",
    "markdown.code_block": "yellow",
    "markdown.link": "underline blue",
    "markdown.link_url": "underline blue",
    "markdown.item.bullet": "bright_cyan",
    "markdown.item.number": "bright_cyan",
    "markdown.block_quote": "italic dim",
    "markdown.hr": "dim cyan",
})


def model_section(label, text, enabled, color="cyan", muted=False):
    text = str(text or "")
    if not enabled or os.environ.get("A1_MARKDOWN", "1").lower() in {"0", "false", "off"}:
        return None
    if len(text) < 80 and not re.search(r"[\n#*`|>\[\]]|^\s*[-+] ", text):
        return None
    output = io.StringIO()
    width = max(20, min(110, shutil.get_terminal_size((80, 24)).columns))
    console = Console(
        file=output,
        force_terminal=True,
        color_system="standard",
        no_color=False,
        width=width,
        theme=THEME,
        highlight=False,
    )
    console.print(Text(label, style=f"bold {color}"))
    console.print(Markdown(text, code_theme="ansi_dark", hyperlinks=False), style="dim" if muted else None)
    return "\n" + output.getvalue().rstrip() + "\n"
