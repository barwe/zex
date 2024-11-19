import os
import sys


def get_default_logger():
    level = os.environ.get("ZEX_LOG_LEVEL", "INFO")
    try:
        from loguru import logger

        logger.remove()
        logger.add(sys.stdout, level=level)
    except ImportError:
        import logging as logger

        logger.basicConfig(
            level=logger._nameToLevel[level],
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    return logger


logger = get_default_logger()
