import traceback
from datetime import datetime

from config import LOG_PATH

from pocketflow import BaseNode as PocketFlowBaseNode


class BaseNode(PocketFlowBaseNode):
    def run(self, shared):
        try:
            prep_res = self.prep(shared)
            exec_res = self._exec(prep_res)
            post_res = self.post(shared, prep_res, exec_res)
            shared["last_error"] = None
            return post_res
        except Exception as exc:
            self._record_exception(shared, exc)
            return "error"

    def _record_exception(self, shared, exc):
        node_name = self.__class__.__name__
        message = f"{node_name}: {exc}"
        shared["last_error"] = message
        print(f"ERROR | {message}")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as log_file:
            log_file.write(f"\n{timestamp} | ERROR | {message}\n")
            log_file.write(traceback.format_exc())
