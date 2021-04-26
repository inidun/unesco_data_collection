import os
from pathlib import Path
from typing import List, Optional, Union

import argh
from argh import arg

from courier.extract.interface import ITextExtractor
from courier.extract.pdfbox_extractor import PDFBoxExtractor
from courier.extract.pdfminer_extractor import PDFMinerExtractor
from courier.extract.pdfplumber_extractor import PDFPlumberExtractor
from courier.extract.tesseract_extractor import TesseractExtractor
from courier.extract.utils import get_filenames


def get_extractor(method: str) -> ITextExtractor:
    if method == 'PDFBox':
        return PDFBoxExtractor()
    if method == 'PDFMiner':
        return PDFMinerExtractor()
    if method == 'PDFPlumber':
        return PDFPlumberExtractor()
    if method == 'Tesseract':
        return TesseractExtractor()
    raise ValueError(method)


@arg('--method', choices=['PDFBox', 'PDFMiner', 'PDFPlumber', 'Tesseract'])  # type: ignore
def extract_text(
    input_path: Union[str, os.PathLike],
    output_folder: Union[str, os.PathLike],
    first_page: int = 1,
    last_page: Optional[int] = None,
    method: str = 'PDFBox',
) -> None:

    Path(output_folder).mkdir(exist_ok=True)
    files: List[Path] = get_filenames(input_path)

    if last_page is not None:
        last_page = int(last_page)

    extractor: ITextExtractor = get_extractor(method)
    extractor.extract(files, output_folder, first_page=first_page, last_page=last_page)


if __name__ == '__main__':
    argh.dispatch_command(extract_text)
