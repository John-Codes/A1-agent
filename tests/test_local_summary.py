from unittest.mock import Mock, patch

import local_summary


def test_summary_uses_local_chat_and_removes_reasoning():
    response = Mock()
    response.json.return_value = {"message": {"content": "Internal reasoning</think>Back up files first."}}
    with patch.object(local_summary.requests, "post", return_value=response) as post:
        result = local_summary.summarize("Summarize this entry", "qwen3:4b")
    assert result == "Back up files first."
    assert post.call_args.args[0].endswith("/api/chat")
    payload = post.call_args.kwargs["json"]
    assert payload["model"] == "qwen3:4b"
    assert payload["think"] is False
    assert payload["options"]["num_predict"] == 256
