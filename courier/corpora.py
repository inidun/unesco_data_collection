import os
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Literal, Tuple, Union

from tqdm import tqdm

from courier.config import get_config
from courier.extract.java_extractor import ExtractedPages, JavaExtractor
from courier.extract.utils import get_filenames
from courier.utils import flatten

CONFIG = get_config()


class PDFCorporaExtractor:
    def __init__(self) -> None:
        self.extractor = JavaExtractor()
        self.article_index = CONFIG.article_index

    def extract(
        self,
        filename: Union[str, os.PathLike],
        level: Literal['page', 'issue'],
    ) -> Iterable[Tuple[str, str]]:

        basename = Path(filename).stem
        courier_id = basename[:6]
        issue_article_index = CONFIG.get_issue_article_index(courier_id)

        if len(issue_article_index) == 0:
            print(f'{filename} not found in index')
            return

        issue: ExtractedPages = self.extractor.extract_pages(filename)
        article_pages = set(flatten([x['pages'] for x in issue_article_index]))
        year = issue_article_index[0]['year']

        if level == 'issue':
            content: str = '\n'.join([str(p.content) for p in issue.pages if p.pdf_page_number in article_pages])
            yield (f'{year}_{courier_id}.txt', content)

        if level == 'page':
            for page in issue.pages:
                if page.pdf_page_number not in article_pages:
                    continue
                yield (f'{year}_{courier_id}_{page.pdf_page_number:>03d}.txt', str(page.content))

    def extracts(
        self,
        filenames: List[Path],
        level: Literal['page', 'issue'],
    ) -> Iterable[Tuple[str, str]]:

        pbar = tqdm(filenames)
        for filename in pbar:
            pbar.set_description(f'{filename.stem:<10}')
            for x in self.extract(filename, level):
                yield x


def extraxt_raw_corpora(
    folder: Union[str, os.PathLike],
    level: Literal['page', 'issue'],
    target_filename: Union[str, os.PathLike],
) -> None:
    filenames = get_filenames(folder)

    Path(target_filename).parent.mkdir(exist_ok=True, parents=True)

    with zipfile.ZipFile(target_filename, 'w', compression=zipfile.ZIP_DEFLATED) as fp:
        for name, content in PDFCorporaExtractor().extracts(filenames, level):
            fp.writestr(name, content)


if __name__ == '__main__':

    date = datetime.now().strftime('%Y%m%d')

    extraxt_raw_corpora(
        CONFIG.pdf_dir, 'issue', CONFIG.base_data_dir / f'corpora/{date}_courier_issue_corpus_article_pages_only.zip'
    )

    extraxt_raw_corpora(
        CONFIG.pdf_dir, 'page', CONFIG.base_data_dir / f'corpora/{date}_courier_page_corpus_article_pages_only.zip'
    )
