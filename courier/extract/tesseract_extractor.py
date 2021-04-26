import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union

import pytesseract
from pdf2image import convert_from_path
from tqdm import tqdm

from courier.extract.interface import ITextExtractor


@dataclass
class TesseractConfig:
    DPI: int = 30
    FMT: str = 'tiff'


@dataclass
class TesseractExtractor(ITextExtractor):

    dpi: int = TesseractConfig.DPI
    fmt: str = TesseractConfig.FMT

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
        images = convert_from_path(filename, first_page=first_page, last_page=last_page, dpi=self.dpi, fmt=self.fmt)
        for i, image in enumerate(images):
            text_filename = Path(output_folder) / f'{basename}_{i+first_page:04}.txt'
            with open(text_filename, 'w') as fp:
                fp.write(pytesseract.image_to_string(image, lang='eng'))


if __name__ == '__main__':
    pass
