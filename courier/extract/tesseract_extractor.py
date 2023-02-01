import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

import pytesseract
from loguru import logger
from pdf2image import convert_from_path

from courier.extract.interface import ITextExtractor


@dataclass
class TesseractExtractor(ITextExtractor):
    dpi: int = 350
    fmt: str = 'tiff'
    grayscale: bool = True
    use_pdftocairo: bool = True

    tessdata: str = str(Path.home() / 'data/tessdata')
    image_to_string_config: str = f'--oem 1 --psm 1 --tessdata-dir {tessdata}'

    def pdf_to_txt(
        self,
        filename: Union[str, os.PathLike],
        output_folder: Union[str, os.PathLike],
        first_page: int = 1,
        last_page: Optional[int] = None,
    ) -> None:
        basename = Path(filename).stem
        images = convert_from_path(
            filename,
            first_page=first_page,
            last_page=last_page,
            dpi=self.dpi,
            fmt=self.fmt,
            grayscale=self.grayscale,
            use_pdftocairo=self.use_pdftocairo,
        )

        i = 0
        for i, image in enumerate(images):
            text_filename = Path(output_folder) / f'{basename}_{i+first_page:04}.txt'
            with open(text_filename, 'w', encoding='utf-8') as fp:
                fp.write(pytesseract.image_to_string(image, lang='eng', config=self.image_to_string_config))

        logger.success(f'Extracted: {basename}, pages: {i+1}, dpi: {self.dpi}, fmt: {self.fmt}')


if __name__ == '__main__':
    pass
