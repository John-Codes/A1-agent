from nodes.base import BaseNode


class ConsoleNode(BaseNode):
    def exec(self, _):
        try:
            return input("you> ").strip()
        except EOFError:
            return "/quit"

    def post(self, shared, prep_res, exec_res):
        text = exec_res
        command = text.split(maxsplit=1)[0].lower() if text else ""
        shared["pending_response"] = None
        if command in {"/quit", "/exit", "/q"}:
            shared["trigger"] = "quit"
            return "quit"
        if command == "/tick":
            shared["trigger"] = "tick"
            shared["pending_input"] = None
            return "tick"
        if command == "/memory":
            shared["trigger"] = "memory"
            return "memory"
        if command == "/log":
            shared["trigger"] = "log"
            return "log"
        if command == "/search" and len(text.split(maxsplit=1)) > 1:
            shared["trigger"] = "search"
            shared["pending_input"] = text.split(maxsplit=1)[1].strip()
            return "search"
        if not text:
            shared["trigger"] = "empty"
            return "empty"

        shared["trigger"] = "message"
        shared["pending_input"] = text
        return "message"
