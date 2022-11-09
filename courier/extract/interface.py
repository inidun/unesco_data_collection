import abc
import os
import sys
from pathlib import Path
from typing import List, Optional, Union

from loguru import logger
from tqdm import tqdm


class ITextExtractor(abc.ABC):
    @abc.abstractmethod
    def pdf_to_txt(
        self,
        filename: Union[str, os.PathLike],
        output_folder: Union[str, os.PathLike],
        first_page: int = 1,
        last_page: Optional[int] = None,
    ) -> None:
        """Extracts text from PDF-file and saves result as text files (one file per page).

        Args:
            filename (Union[str, os.PathLike]): Input filename (PDF-file)
            output_folder (Union[str, os.PathLike]): Output folder
            first_page (int, optional): First page to extract. Defaults to 1.
            last_page (int, optional): Last page to extract. Defaults to None.
        """

    def batch_extract(
        self,
        files: List[Path],
        output_folder: Union[str, os.PathLike],
        *,
        first_page: int = 1,
        last_page: Optional[int] = None,
    ) -> None:
        """Extracts text from multiple PDF-files and saves result as text files (one file per page).

        Args:
            files (List[Path]): List of PDF-files to process
            output_folder (Union[str, os.PathLike]): Output folder
            first_page (int, optional): First page to extract. Defaults to 1.
            last_page (Optional[int], optional): Last page to extract. Defaults to None.
        """
        logfile = Path(output_folder) / 'extract.log'
        if logfile.exists():
            files = self._skip_completed(files, logfile)
        if len(files) == 0:
            return
        file_logger = self._add_logger(logfile)

        logger.patch(lambda msg: tqdm.write(msg, end=''))
        pbar = tqdm(files, desc='File')
        for filename in pbar:
            pbar.set_description(f'Processing {filename.stem}')
            self.pdf_to_txt(filename, output_folder, first_page, last_page)

        self._remove_logger(file_logger)

    def _add_logger(self, logfile: Union[str, os.PathLike]) -> int:
        logger.configure(handlers=[{'sink': sys.stderr, 'level': 'WARNING'}])
        file_logger = logger.add(
            Path(logfile),
            format='{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}',
        )
        return file_logger

    def _remove_logger(self, file_logger: int) -> None:
        logger.remove(file_logger)
        logger.configure(handlers=[{'sink': sys.stderr, 'level': 'INFO'}])

    def _skip_completed(self, files: List[Path], logfile: Union[str, os.PathLike]) -> List[Path]:
        expr = r'(?P<time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+) \| (?P<lvl>[A-Z]+) \| (?P<msg>\w+: (?P<id>\w+).*)'
        completed = {line['id'] for line in logger.parse(logfile, expr) if line['lvl'] == 'SUCCESS'}
        logger.info(f'Skipping {len(completed)} files: {completed}')
        files = [file for file in files if all(c not in str(file) for c in completed)]
        return files


if __name__ == '__main__':
    pass
