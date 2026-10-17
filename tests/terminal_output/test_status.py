from features.terminal_output.status import status_line


def test_status_line_handles_uppercase_tones():
    # TONES values are uppercase ("RED"); paint() expects lowercase. A tty
    # (enabled=True) previously crashed with KeyError: 'RED'.
    out = status_line("MODEL FAILED", "boom", enabled=True)
    assert "MODEL FAILED |" in out
    assert "boom" in out


def test_highlight_paints_status_tokens_without_crashing():
    from features.terminal_output.status import highlight

    out = highlight("status: done and failed today", True)
    assert "done" in out and "failed" in out
