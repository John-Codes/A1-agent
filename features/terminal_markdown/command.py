import os

DEMO = """## A1 daily work

**Readable answers**, with clear headings and breathing room.

- Author: **Sergio**
- Output: English and Spanish drafts
- Next step: review the saved articles

### Useful commands

```bash
/seo status
/markdown off
```

| Item | Status |
| --- | --- |
| Draft | Ready for review |
| Publishing | Awaiting review |

> This is a display demo. It does not run tools or call a model.
"""


def command(body):
    action = body.strip().lower() or "status"
    if action == "demo":
        return {"kind": "message", "speaker": "master_llm", "response": DEMO}
    if action in {"on", "off"}:
        os.environ["A1_MARKDOWN"] = "1" if action == "on" else "0"
    elif action != "status":
        return {"kind": "error", "error": "Use /markdown on, off, status, or demo."}
    enabled = os.environ.get("A1_MARKDOWN", "1").lower() not in {"0", "false", "off"}
    return {
        "kind": "text",
        "text": f"Markdown {'on' if enabled else 'off'} for this session. "
        "Requires a color terminal; NO_COLOR and redirected output stay plain. Try /markdown demo.",
    }
