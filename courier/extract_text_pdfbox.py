import os
from pathlib import Path
from typing import List, Union

import argh
import pdfbox

from courier.config import CourierConfig

CONFIG = CourierConfig()


def get_filenames(files: Union[str, os.PathLike]) -> List[Path]:
    items = []
    path = Path(files)
    if path.is_dir():
        items = list(path.glob("*.pdf"))
    elif path.is_file() and path.suffix == ".pdf":
        items.append(path)
    return items


# FIXME: use python modeule instead of OS commands
def get_number_of_pages(filename: Union[str, os.PathLike]) -> int:
    cmd = f"pdfinfo {filename} | grep 'Pages' | awk '{{print $2}}'"
    num_pages = int(os.popen(cmd).read().strip())
    return num_pages


def extract_text(files: Union[str, os.PathLike], output_folder: Union[str, os.PathLike]) -> None:

    Path(output_folder).mkdir(exist_ok=True)
    p = pdfbox.PDFBox()

    for filename in get_filenames(files):
        num_pages = get_number_of_pages(filename)
        for page in range(1, num_pages + 1):
            output_filename = Path(output_folder) / f"{Path(filename).stem}_{page:04}.txt"
            p.extract_text(filename, output_path=output_filename, start_page=page, end_page=page, console=False)
        print(f" {os.path.basename(filename)} {num_pages}")


if __name__ == "__main__":
    argh.dispatch_command(extract_text)
