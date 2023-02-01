import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union

# TODO: No pdf2image, get page numbers from Java
import pdf2image

# TODO: Create new courier_pdfbox class, replace this
import pdfbox
from loguru import logger

from courier.extract.interface import ITextExtractor


@dataclass
class PDFBoxExtractor(ITextExtractor):
    p: pdfbox.PDFBox = pdfbox.PDFBox()
    encoding: str = 'utf-8'
    html: bool = False
    sort: bool = False
    ignore_beads: bool = False
    console: bool = False

    def pdf_to_txt(
        self,
        filename: Union[str, os.PathLike],
        output_folder: Union[str, os.PathLike],
        first_page: int = 1,
        last_page: Optional[int] = None,
    ) -> None:
        basename = Path(filename).stem
        # TODO Remove num_pages
        num_pages = pdf2image.pdfinfo_from_path(filename)['Pages']
        if last_page is None or last_page > num_pages:
            last_page = int(num_pages)

        # TODO
        # for page in p.get_pages('filename'): -> sorted list of strings (or list of strings + titles, or markup)
        for page in range(first_page, last_page + 1):
            output_filename = Path(output_folder) / f'{basename}_{page:04}.txt'
            self.p.extract_text(
                filename,
                output_path=output_filename,
                encoding=self.encoding,
                html=self.html,
                sort=self.sort,
                ignore_beads=self.ignore_beads,
                start_page=page,
                end_page=page,
                console=self.console,
            )
        # FIXME: Report correct number of pages. Should be `last_page - first_page + 1`
        logger.success(f'Extracted: {basename}, pages: {num_pages}')

    def batch_extract(
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


if __name__ == '__main__':
    pass
