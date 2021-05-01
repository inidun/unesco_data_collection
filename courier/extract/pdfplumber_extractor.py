import os
from pathlib import Path
from typing import List, Optional, Union

import pdfplumber
from tqdm import tqdm

from courier.extract.interface import ITextExtractor


class PDFPlumberExtractor(ITextExtractor):
    def extract(
        self,
        files: List[Path],
        output_folder: Union[str, os.PathLike],
        *,
        first_page: int = 1,
        last_page: Optional[int] = None,
    ) -> None:
        pbar = tqdm(files, desc='File')
        for filename in pbar:
            pbar.set_description(f'Processing {filename.stem}')
            self.pdf_to_txt(filename, output_folder, first_page, last_page)

    def pdf_to_txt(
        self,
        filename: Union[str, os.PathLike],
        output_folder: Union[str, os.PathLike],
        first_page: int = 1,
        last_page: Optional[int] = None,
    ) -> None:
        basename = Path(filename).stem
        with pdfplumber.open(filename) as pdf:
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
                    with open(Path(output_folder) / f'{basename}_{i+1:04}.txt', 'w') as fp:
                        fp.write(data)


if __name__ == '__main__':
    pass
