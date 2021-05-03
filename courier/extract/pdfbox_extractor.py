import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union

import pdf2image
import pdfbox
from loguru import logger

from courier.extract.interface import ITextExtractor


@dataclass
class PDFBoxExtractor(ITextExtractor):

    p: pdfbox.PDFBox = pdfbox.PDFBox()

    def extract(
        self,
        files: List[Path],
        output_folder: Union[str, os.PathLike],
        *,
        first_page: int = 1,
        last_page: Optional[int] = None,
    ) -> None:

        logfile = Path(output_folder) / 'extract.log'
        if logfile.exists():
            files = self._skip_completed(files, logfile)
        if len(files) == 0:
            return
        file_logger = self._add_logger(logfile)

        total_files = len(files)
        for i, filename in enumerate(files, start=1):
            print(f'Processing {filename.stem}\t{i:03}/{total_files}', end='\r')
            self.pdf_to_txt(filename, output_folder, first_page, last_page)

        self._remove_logger(file_logger)

    def pdf_to_txt(
        self,
        filename: Union[str, os.PathLike],
        output_folder: Union[str, os.PathLike],
        first_page: int = 1,
        last_page: Optional[int] = None,
    ) -> None:
        basename = Path(filename).stem
        num_pages = pdf2image.pdfinfo_from_path(filename)['Pages']
        if last_page is None or last_page > num_pages:
            last_page = int(num_pages)
        for page in range(first_page, last_page + 1):
            output_filename = Path(output_folder) / f'{basename}_{page:04}.txt'
            self.p.extract_text(
                filename,
                output_path=output_filename,
                start_page=page,
                end_page=page,
                console=False,
                encoding='utf-8',
            )
        logger.success(f'Extracted: {basename}, pages: {num_pages}')


if __name__ == '__main__':
    pass
