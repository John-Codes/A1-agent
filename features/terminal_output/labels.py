LABEL_COLORS = {
    "DATA": "magenta",
    "ERROR": "red",
    "INFO": "blue",
    "MasterLLM": "cyan",
    "SubLLM": "magenta",
    "SUCCESS": "green",
    "WARNING": "yellow",
    "YOU": "green",
}


def llm_label(result, suffix=None):
    speaker = result.get("speaker", "master_llm")
    if speaker != "sub_llm":
        return _suffix("MasterLLM", suffix)
    identity = result.get("speaker_name") or result.get("speaker_index")
    base = f"SubLLM[{identity}]" if identity is not None else "SubLLM"
    return _suffix(base, suffix)


def color_for(label):
    base = label.split("[", 1)[0]
    return LABEL_COLORS.get(base, "blue")


def _suffix(label, suffix):
    return f"{label}[{suffix}]" if suffix else label
