import os
from pathlib import Path
from typing import Optional, Union

import argh
import pytesseract
from pdf2image import convert_from_path
from tqdm import tqdm

from courier.config import CourierConfig
from courier.utils import get_filenames

CONFIG = CourierConfig()

DPI = 300
FMT = "tiff"


def extract_text(
    files: Union[str, os.PathLike],
    output_folder: Union[str, os.PathLike],
    first_page: int = 1,
    last_page: Optional[int] = None,
    dpi: int = DPI,
    fmt: str = FMT,
) -> None:

    Path(output_folder).mkdir(exist_ok=True)

    for filename in tqdm(get_filenames(files), desc="Extracting"):
        basename = Path(filename).stem
        images = convert_from_path(filename, dpi=dpi, first_page=first_page, last_page=last_page, fmt=fmt)

        for i, image in enumerate(images):
            text_filename = Path(output_folder) / f"{basename}_{i+first_page:04}.txt"
            with open(text_filename, "w") as fp:
                fp.write(pytesseract.image_to_string(image, lang="eng"))


if __name__ == "__main__":
    argh.dispatch_command(extract_text)
