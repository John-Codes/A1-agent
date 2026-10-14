import logging
import os

from tools.log import log_tool_event


class GatewayHandler(logging.Handler):
    def emit(self, record):
        log_tool_event(record.name, record.levelname.lower(), self.format(record))


def configure_logging():
    os.environ["BROWSER_USE_SETUP_LOGGING"] = "false"
    for name in ("browser_use", "bubus", "cdp_use"):
        logger = logging.getLogger(name)
        if not any(isinstance(handler, GatewayHandler) for handler in logger.handlers):
            logger.handlers = [GatewayHandler()]
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
