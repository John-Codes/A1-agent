import re


THINK_BLOCK = re.compile(
    r"^\s*<think>\s*(.*?)\s*</think>\s*(.*)$",
    re.DOTALL | re.IGNORECASE,
)


def split_thinking(text):
    match = THINK_BLOCK.match(str(text or ""))
    if not match:
        return "", str(text or "")
    return match.group(1).strip(), match.group(2).strip()
