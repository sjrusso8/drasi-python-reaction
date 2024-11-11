import logging
import sys


def _config_logger():
    logger = logging.getLogger("drasi_python_reaction.sdk")
    logger.setLevel(logging.DEBUG)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)

    logger.addHandler(stdout_handler)

    return logger


logger = _config_logger()
