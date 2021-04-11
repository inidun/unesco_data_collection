import io
import os
import re
import warnings
from dataclasses import dataclass
from typing import Iterator, List, Tuple, Union

import pandas as pd
import untangle

from courier.config import get_config
from courier.utils import get_double_pages

CONFIG = get_config()


def read_xml(filename: Union[str, bytes, os.PathLike]) -> untangle.Element:
    with open(filename, 'r') as fp:
        content = fp.read()
        content = CONFIG.invalid_chars.sub('', content)
        xml = io.StringIO(content)
        element = untangle.parse(xml)
        return element


def get_issue_index(courier_id: str) -> pd.DataFrame:
    return CONFIG.article_index.loc[CONFIG.article_index['courier_id'] == courier_id]


def get_issue_content(courier_id: str) -> untangle.Element:
    # if len(courier_id) != 6:
    #     raise ValueError(f'Not a valid courier id "{courier_id}')
    # if courier_id not in CONFIG.article_index.courier_id:
    #     raise ValueError(f'{courier_id} not in article index')
    return read_xml(list(CONFIG.pdfbox_xml_dir.glob(f'{courier_id}*.xml'))[0])


@dataclass(order=True, frozen=True)
class Page:
    page_number: int
    text: str

    def __post_init__(self) -> None:
        object.__setattr__(self, 'text', str(self.text))


class Article:
    def __init__(self, record: dict, courier_issue: 'CourierIssue'):
        self.article_metadata = record
        self.courier_issue = courier_issue

    @property
    def pages(self) -> Iterator[Page]:
        for page_number in self.article_metadata['pages']:
            yield self.courier_issue.get_page(page_number)

    @property
    def courier_id(self) -> str:
        return self.article_metadata['courier_id']

    @property
    def record_number(self) -> str:
        return self.article_metadata['record_number']

    @property
    def title(self) -> str:
        return self.article_metadata['catalogue_title']

    @property
    def year(self) -> str:
        return self.article_metadata['year']

    @property
    def publication_date(self) -> str:
        return self.article_metadata['publication_date']


class CourierIssue:
    def __init__(self, courier_id: str):
        self.index = get_issue_index(courier_id)
        self.content = get_issue_content(courier_id)
        self.double_pages = get_double_pages(courier_id)

        # FIXME: Add error checking, but tests must be updated
        # if len(courier_id) != 6:
        #     raise ValueError(f'Not a valid courier id "{courier_id}')
        # if courier_id not in CONFIG.article_index.courier_id:
        #     raise ValueError(f'{courier_id} not in article index')

    @property
    def articles(self) -> Iterator[Article]:
        with warnings.catch_warnings():
            warnings.simplefilter(action='ignore', category=FutureWarning)
            for record in self.index.to_dict('record'):
                yield Article(record, self)

    @property
    def num_articles(self) -> int:
        return len(self.index)

    @property
    def num_pages(self) -> int:
        return len(self.content.document.page)

    def get_page(self, page_number: int) -> Page:
        page_delta = len([x for x in self.double_pages if x < page_number])
        pages = [p for p in self.content.document.page if p['number'] == str(page_number - page_delta)]
        return Page(page_number, pages[0].cdata if len(pages) > 0 else '')

    def find_pattern(self, pattern: str) -> List[Tuple[int, int]]:
        page_numbers = []
        for i, page in enumerate(self.content.document.page, 1):
            m = re.search(pattern, page.cdata, re.IGNORECASE)
            if m:
                page_numbers.append((i, page['number']))
        return page_numbers
