import os
from pathlib import Path
from typing import List, Union


def get_filenames(files: Union[str, os.PathLike], extension: str = 'pdf') -> List[Path]:
    items = []
    path = Path(files)
    if path.is_dir():
        items = list(path.glob(f'*.{extension}'))
    elif path.is_file() and path.suffix == f'.{extension}':
        items.append(path)
    return items


if __name__ == '__main__':
    pass
