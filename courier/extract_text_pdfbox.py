import os
from pathlib import Path
from typing import Union

import argh
import pdf2image
import pdfbox

from courier.config import CourierConfig
from courier.utils import get_filenames

CONFIG = CourierConfig()


# TOOD: log
def extract_text(files: Union[str, os.PathLike], output_folder: Union[str, os.PathLike]) -> None:

    Path(output_folder).mkdir(exist_ok=True)
    p = pdfbox.PDFBox()

    for filename in get_filenames(files):
        num_pages = pdf2image.pdfinfo_from_path(filename)["Pages"]
        for page in range(1, num_pages + 1):
            output_filename = Path(output_folder) / f"{Path(filename).stem}_{page:04}.txt"
            p.extract_text(filename, output_path=output_filename, start_page=page, end_page=page, console=False)
        print(f" {os.path.basename(filename)} {num_pages}")


# TODO: get_page(file: Union[str, os.PathLike], page_number: int) -> str
# Use tempdir/tempfile

# TODO: get_pages(file: Union[str, os.PathLike], pages: list) -> str
# Use tempdir

if __name__ == "__main__":
    argh.dispatch_command(extract_text)
