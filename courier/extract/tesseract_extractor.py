import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

import pytesseract
from loguru import logger
from pdf2image import convert_from_path

from courier.extract.interface import ITextExtractor


@dataclass
class TesseractConfig:
    DPI: int = 300
    FMT: str = 'tiff'


@dataclass
class TesseractExtractor(ITextExtractor):

    dpi: int = TesseractConfig.DPI
    fmt: str = TesseractConfig.FMT

    def pdf_to_txt(
        self,
        filename: Union[str, os.PathLike],
        output_folder: Union[str, os.PathLike],
        first_page: int = 1,
        last_page: Optional[int] = None,
    ) -> None:
        basename = Path(filename).stem
        images = convert_from_path(filename, first_page=first_page, last_page=last_page, dpi=self.dpi, fmt=self.fmt)

        i = 0
        for i, image in enumerate(images):
            text_filename = Path(output_folder) / f'{basename}_{i+first_page:04}.txt'
            with open(text_filename, 'w') as fp:
                fp.write(pytesseract.image_to_string(image, lang='eng'))

        logger.success(f'Extracted: {basename}, pages: {i+1}, dpi: {self.dpi}, fmt: {self.fmt}')


if __name__ == '__main__':
    pass
