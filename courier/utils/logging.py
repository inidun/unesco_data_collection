import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Union

from loguru import logger
from tqdm import tqdm


@contextmanager
def file_logger(logfile: Union[str, os.PathLike], **kwargs) -> Generator:  # type: ignore
    logger.patch(lambda msg: tqdm.write(msg, end=''))
    try:
        name = Path(logfile).stem
        handler = logger.add(Path(logfile), filter=lambda record: record['extra']['task'] == name, **kwargs)
        yield logger.bind(task=name)
    finally:
        logger.remove(handler)


if __name__ == '__main__':
    pass
