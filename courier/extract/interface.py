import abc
import os
from pathlib import Path
from typing import List, Optional, Union


class ITextExtractor(abc.ABC):

    # TODO: Rename
    @abc.abstractmethod
    def extract(
        self,
        files: List[Path],
        output_folder: Union[str, os.PathLike],
        *,
        first_page: int = 1,
        last_page: Optional[int] = None,
    ) -> None:
        """Extracts text from multiple PDF-files and saves result as text files (one file per page).

        Args:
            files (List[Path]): List of PDF-files to process
            output_folder (Union[str, os.PathLike]): Output folder
            first_page (int, optional): First page to extract. Defaults to 1.
            last_page (Optional[int], optional): Last page to extract. Defaults to None.
        """

    @abc.abstractmethod
    def pdf_to_txt(
        self,
        filename: Union[str, os.PathLike],
        output_folder: Union[str, os.PathLike],
        first_page: int = 1,
        last_page: int = None,
    ) -> None:
        """Extracts text from PDF-file and saves result as text files (one file per page).

        Args:
            filename (Union[str, os.PathLike]): Input filename (PDF-file)
            output_folder (Union[str, os.PathLike]): Output folder
            first_page (int, optional): First page to extract. Defaults to 1.
            last_page (int, optional): Last page to extract. Defaults to None.
        """


if __name__ == '__main__':
    pass
