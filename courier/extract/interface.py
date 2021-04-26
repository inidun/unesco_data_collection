import abc
import os
from pathlib import Path
from typing import List, Optional, Union


class ITextExtractor(abc.ABC):
    @abc.abstractmethod
    def extract(
        self,
        files: List[Path],
        output_folder: Union[str, os.PathLike],
        *,
        first_page: int = 1,
        last_page: Optional[int] = None,
    ) -> None:
        ...  # pragma: no cover

    @abc.abstractmethod
    def file_to_txt(
        self,
        filename: Union[str, os.PathLike],
        output_folder: Union[str, os.PathLike],
        first_page: int = 1,
        last_page: int = None,
    ) -> None:
        ...  # pragma: no cover


if __name__ == '__main__':
    pass
