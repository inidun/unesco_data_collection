import os
from pathlib import Path
from typing import Optional, Union

import argh
import pytesseract
from pdf2image import convert_from_path
from tqdm import tqdm

from courier.utils import get_filenames

DPI = 300
FMT = 'tiff'


# TODO: Add logger
# TODO: Expose `pdf2image.convert_from_path`-arguments
# TODO: Log `pdf2image.convert_from_path`-arguments
# TODO: Expose `pytesseract.image_to_string`-arguments
# TODO: Log `pytesseract.image_to_string`-arguments


def extract_text(
    files: Union[str, os.PathLike],
    output_folder: Union[str, os.PathLike],
    first_page: int = 1,
    last_page: Optional[int] = None,
    dpi: int = DPI,
    fmt: str = FMT,
) -> None:

    Path(output_folder).mkdir(exist_ok=True)

    for filename in tqdm(get_filenames(files), desc='Extracting'):
        basename = Path(filename).stem
        images = convert_from_path(filename, dpi=dpi, first_page=first_page, last_page=last_page, fmt=fmt)

        for i, image in enumerate(images):
            text_filename = Path(output_folder) / f'{basename}_{i+first_page:04}.txt'
            with open(text_filename, 'w') as fp:
                fp.write(pytesseract.image_to_string(image, lang='eng'))


# TODO: get_page(file: Union[str, os.PathLike], page_number: int) -> str

# TODO: get_pages(file: Union[str, os.PathLike], pages: list) -> str

if __name__ == '__main__':
    argh.dispatch_command(extract_text)
