import os
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Union

from loguru import logger
from tqdm import tqdm


@contextmanager
def file_logger(logfile: Union[str, os.PathLike], **kwargs) -> Generator:  # type: ignore
    try:
        logger.configure(handlers=[{'sink': sys.stderr, 'level': 'WARNING'}])
        handler = logger.add(Path(logfile), **kwargs)
        logger.patch(lambda msg: tqdm.write(msg, end=''))
        yield
    finally:
        logger.remove(handler)
        logger.configure(handlers=[{'sink': sys.stderr, 'level': 'INFO'}])