from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / ".a1-email-emergency-stop"


def active():
    return PATH.exists()


def trigger(reason):
    PATH.write_text(reason[:2000] + "\n", encoding="utf-8")


def clear():
    PATH.unlink(missing_ok=True)
