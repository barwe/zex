import os
import sys
import json
from os.path import exists
from .types import Union, T

json_load = json.load
json_loads = json.loads
json_dump = json.dumps
json_dumps = json.dumps


def read(filepath: str):
    with open(filepath) as fr:
        return fr.read()


def write(content: Union[bytes, str], filepath: str, mode=None):
    mode = mode or ("wb" if isinstance(content, bytes) else "w")
    with open(filepath, mode) as fw:
        fw.write(content)


def read_json(filepath: str, default=None):
    if not exists(filepath):
        return default
    with open(filepath) as fr:
        return json.load(fr)


def write_json(data: T, filepath: str, **options):
    with open(filepath, "w") as fw:
        json.dump(data, fw, **options)


def get_default_logger():
    level = os.environ.get("TGRPC_LOG_LEVEL", "DEBUG")

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
