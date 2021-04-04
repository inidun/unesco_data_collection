import os
from pathlib import Path
from typing import List, Union


def get_filenames(files: Union[str, os.PathLike]) -> List[Path]:
    items = []
    path = Path(files)
    if path.is_dir():
        items = list(path.glob("*.pdf"))
    elif path.is_file() and path.suffix == ".pdf":
        items.append(path)
    return items
