import logging


class Logger:
    def __init__(self, name: str) -> None:
        self.logger = logging.getLogger(name)
        logging.basicConfig(level=logging.ERROR,
                            format="%(asctime)s %(levelname)s [%(name)s] - %(message)s")

    def info(self, message: str):
        self.logger.info(message)

    def debug(self, message: str):
        self.logger.debug(message)

    def error(self, message: str):
        self.logger.error(message)

    def exception(self, message: str):
        self.logger.exception(message)

    def critical(self, message: str):
        self.logger.critical(message)
