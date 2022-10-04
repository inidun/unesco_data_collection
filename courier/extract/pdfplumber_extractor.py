import os
from pathlib import Path
from typing import Optional, Union

import pdfplumber
from loguru import logger

from courier.extract.interface import ITextExtractor


class PDFPlumberExtractor(ITextExtractor):
    def pdf_to_txt(
        self,
        filename: Union[str, os.PathLike],
        output_folder: Union[str, os.PathLike],
        first_page: int = 1,
        last_page: Optional[int] = None,
    ) -> None:
        basename = Path(filename).stem
        with pdfplumber.open(filename) as pdf:  # type: ignore[arg-type]
            num_pages = len(pdf.pages)
            if last_page is None or last_page > num_pages:
                last_page = len(pdf.pages)
            pages = range(first_page - 1, last_page)
            for i in pages:
                page = pdf.pages[i]
                if page is not None:
                    data = page.extract_text()
                    if data is None:
                        data = ''
                    with open(Path(output_folder) / f'{basename}_{i+1:04}.txt', 'w', encoding='utf-8') as fp:
                        fp.write(data)
        logger.success(f'Extracted: {basename}, pages: {num_pages}')


if __name__ == '__main__':
    pass
