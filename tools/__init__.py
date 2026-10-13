__all__ = ["dispatch_tool_call", "parse_tool_calls", "strip_tool_calls", "tool_names"]


def __getattr__(name):
    if name in __all__:
        from tools import dispatcher
        return getattr(dispatcher, name)
    raise AttributeError(name)
