from tools.log import brief_error, log_exception

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
        shared["last_error"] = brief_error(node_name, exc)
        log_exception(node_name, exc)
