import os
from io import StringIO
from pathlib import Path
from typing import List, Optional, Union

import pdf2image
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from tqdm import tqdm

from courier.extract.interface import ITextExtractor


class PDFMinerExtractor(ITextExtractor):
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
            self.file_to_txt(filename, output_folder, first_page, last_page)

    def file_to_txt(
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
        pagestr = StringIO()
        with open(filename, 'rb') as fp_in:
            parser = PDFParser(fp_in)
            doc = PDFDocument(parser)
            rsrcmgr = PDFResourceManager()
            device = TextConverter(rsrcmgr, pagestr, laparams=LAParams())
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            for i, page in enumerate(PDFPage.create_pages(doc)):
                if i not in range(first_page - 1, last_page):
                    continue
                interpreter.process_page(page)
                with open(Path(output_folder) / f'{basename}_{i+1:04}.txt', 'w') as fp_out:
                    fp_out.write(pagestr.getvalue())
                pagestr.truncate(0)
                pagestr.seek(0)


if __name__ == '__main__':
    pass
