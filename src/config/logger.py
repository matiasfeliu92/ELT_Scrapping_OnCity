import logging

class LoggerConfig:
    _logger = None

    @classmethod
    def get_logger(cls, name: str = "mi_app") -> logging.Logger:
        if cls._logger is None:
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            cls._logger = logging.getLogger(name)
        return cls._logger