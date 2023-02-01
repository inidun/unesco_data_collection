import re
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

import ftfy

from courier.config import get_config
from courier.extract.java_extractor import ExtractedPages, JavaExtractor
from courier.utils import flatten

CONFIG = get_config()

CASE = {
    0: 'One article on page',
    1: '2 articles - 1 starts before page, 2 start on page',
    2: '2 articles - 2 starts before page, 1 start on page',
    3: '2 articles - Both start on page',
    4: '2 articles - None start on page',
    5: '> 2 articles - Unhandled',
}


@dataclass
class ExtractionError:
    article: 'Article'
    year: Optional[int] = field(init=False)
    courier_id: Optional[str] = field(init=False)
    record_number: Optional[int] = field(init=False)
    page: int
    case: int
    error: str = field(init=False)
    title: str = field(init=False)
    comment: Optional[str] = None

    def __post_init__(self) -> None:
        self.year = self.article.year
        self.courier_id = self.article.courier_id
        self.record_number = self.article.record_number
        self.error = CASE[self.case]
        self.title = self.article.catalogue_title

    def __str__(self) -> str:
        s = f'Page {self.page}: {CASE[self.case]}'
        if self.comment:
            s += '\n\t' + self.comment
        return s

    def __repr__(self) -> str:
        return str(self)

    @property
    def asdict(self) -> Dict[str, Any]:
        return asdict(self)


class Page:
    def __init__(
        self,
        page_number: int,
        text: str,
        titles: Optional[List[Tuple[str, int]]] = None,
        articles: Optional[List['Article']] = None,
    ):
        self.page_number: int = page_number
        self.text: str = str(text)
        self.titles: List[Tuple[int, str]] = self.cleanup_titles(titles) if titles is not None else []
        self.articles: List['Article'] = articles or []
        self.errors: List[ExtractionError] = []

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return str(self)

    # FIXME: Remove
    @property
    def number_of_articles(self) -> int:
        return len(self.articles)

    def cleanup_titles(self, titles: List[Tuple[str, int]]) -> List[Tuple[int, str]]:
        if titles is None:
            return []
        titles = [(position, ftfy.fix_text(title)) for title, position in titles]
        titles = [(position, ' '.join([x for x in title.split() if len(x) > 1])) for position, title in titles]
        return titles

    def get_pritty_titles(self) -> str:
        return '\n'.join([f'\t{position}:\t"{title}"' for position, title in self.titles])


@dataclass
class DoubleSpreadRightPage(Page):
    def __init__(self, page_number: int):
        super().__init__(page_number=page_number, text='', titles=None)


class Article:
    def __init__(
        self,
        courier_issue: 'CourierIssue',
        courier_id: Optional[str] = None,
        year: Optional[int] = None,
        record_number: Optional[int] = None,
        pages: Optional[List[int]] = None,
        catalogue_title: Optional[str] = None,
        authors: Optional[str] = None,
    ):
        self.courier_issue: 'CourierIssue' = courier_issue
        self.courier_id: Optional[str] = courier_id
        self.year: Optional[int] = year
        self.record_number: Optional[int] = record_number
        self.page_numbers: List[int] = pages or []  # TODO: Change name of pages in article_index page_numbers
        self.catalogue_title: str = catalogue_title or ''
        self.authors: str = authors or ''
        self.pages: List[Page] = []
        self.texts: List[Tuple[int, str]] = []
        self.errors: List[str] = []

    def __repr__(self) -> str:
        return self.catalogue_title

    # FIXME: Check this
    @property
    def min_page_number(self) -> int:
        return 0 if self.page_numbers is None else min(self.page_numbers)

    # FIXME: Check this
    @property
    def max_page_number(self) -> int:
        return 0 if self.page_numbers is None else max(self.page_numbers)

    def get_text(self) -> str:
        text: str = ''
        text += f'Title:\t{self.catalogue_title}\n'
        text += f'Pages:\t{",".join(str(x) for x in self.page_numbers)}\n'

        missing_pages = self.get_not_found_pages()
        if missing_pages:
            text += f'Missing: {",".join(str(x) for x in missing_pages)}\n\n'

        text += '\n'.join(self.errors)
        text += '\n'

        for page_number, page_text in self.texts:
            text += f'\n{20*"-"} Page {page_number} {20*"-"}\n\n{page_text}\n'
        return text

    def get_assigned_pages(self) -> Set[int]:
        return {p[0] for p in self.texts}

    def get_not_found_pages(self) -> Set[int]:
        return {x for x in self.page_numbers if x not in self.get_assigned_pages()}

    @property
    def filename(self) -> str:
        safe_title = re.sub(r'[^\w]+', '_', str(self.catalogue_title).lower())
        return f'{self.year or "0000"}_{self.courier_id}_{self.record_number}_{safe_title[:60]}.txt'

    # FIXME: Use repr
    @property
    def record(self) -> str:
        return f'{self.courier_id};{self.year};{self.record_number};{len(self.get_assigned_pages())};{len(self.get_not_found_pages())};{len(self.page_numbers)}'


class CourierIssue:
    def __init__(self, courier_id: str):
        self.courier_id = courier_id

        if len(courier_id) != 6:
            raise ValueError(f'Not a valid courier id "{courier_id}')

        if courier_id not in CONFIG.article_index.courier_id.values:
            raise ValueError(f'{courier_id} not in article index')

        self.articles: List[Article] = self._get_articles()

        self._pdf_double_page_numbers: List[int] = CONFIG.double_pages.get(courier_id, [])

        self.double_pages: List[int] = [x + i for i, x in enumerate(self._pdf_double_page_numbers)]

        self.pages: List[Page] = PagesExtractor().extract(self)

    def __repr__(self) -> str:
        return self.courier_id

    def to_pdf_page_number(self, page_number: int) -> int:
        _pdf_page_number = page_number - 1 - len([x for x in self.double_pages if x < page_number])
        return _pdf_page_number

    def get_article(self, record_number: int) -> Optional[Article]:
        return next((x for x in self.articles if x.record_number == record_number), None)

    def get_article_from_title(self, title: str) -> Optional[Article]:
        return next((x for x in self.articles if x.catalogue_title == title), None)

    def _get_articles(self) -> List[Article]:
        articles: List[Article] = [
            Article(courier_issue=self, **items) for items in CONFIG.get_issue_article_index(self.courier_id)
        ]
        return articles

    @property
    def num_articles(self) -> int:
        return len(self.articles)

    def __len__(self) -> int:
        return len(self.pages)

    def __getitem__(self, index: int) -> Page:
        return self.pages[index]

    def get_page(self, page_number: int) -> Page:
        return self[page_number - 1]

    def get_assigned_pages(self) -> Set[int]:
        return {p.page_number for p in self.pages if len(p.articles) != 0}

    def get_consolidated_pages(self) -> Set[int]:
        return set.union(*[p.get_assigned_pages() for p in self.articles])

    def get_article_pages(self) -> Set[int]:
        return set(flatten([a.page_numbers for a in self.articles]))


class PagesExtractor:
    def extract(self, issue: CourierIssue) -> List[Page]:
        """Returns extracted page content"""

        filename: str = CONFIG.get_issue_filename(issue.courier_id)
        content: ExtractedPages = JavaExtractor().extract_pages(filename)

        num_pages = len(content.pages) + len(issue.double_pages)

        pages = [
            DoubleSpreadRightPage(page_number)
            if page_number - 1 in issue.double_pages
            else Page(
                page_number=page_number,
                text=content.pages[issue.to_pdf_page_number(page_number)].content,
                titles=content.pages[issue.to_pdf_page_number(page_number)].titles,
            )
            for page_number in range(1, num_pages + 1)
        ]
        return pages


if __name__ == '__main__':
    pass
