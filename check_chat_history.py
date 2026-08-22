import json

from chat_history_diagnostics import chat_history_diagnostics


if __name__ == "__main__":
    print(json.dumps(chat_history_diagnostics(), indent=2, sort_keys=True))
