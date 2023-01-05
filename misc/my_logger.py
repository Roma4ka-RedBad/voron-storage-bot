import logging
from loguru import logger


class LoguruHandler(logging.Handler):
    LEVEL_MAPS = {
        logging.CRITICAL: "CRITICAL",
        logging.ERROR: "ERROR",
        logging.WARNING: "WARNING",
        logging.INFO: "INFO",
        logging.DEBUG: "DEBUG"
    }

    def _get_level(self, record: logging.LogRecord):
        return self.LEVEL_MAPS.get(record.levelno, record.levelno)

    def emit(self, record: logging.LogRecord) -> None:
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(self._get_level(record), record.getMessage())

