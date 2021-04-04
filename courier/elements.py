import io
import os
import re
import warnings
from typing import Iterator, List, Tuple, Union

import untangle

from courier.config import CourierConfig

CONFIG = CourierConfig()


def read_xml(filename: Union[str, bytes, os.PathLike]) -> untangle.Element:
    with open(filename, "r") as fp:
        content = fp.read()
        content = CONFIG.invalid_chars.sub("", content)
        xml = io.StringIO(content)
        element = untangle.parse(xml)
        return element


class Page:
    def __init__(self, page_number: int, text: str):
        self.page_number = page_number
        self.text = text

    def __repr__(self) -> str:
        return repr(self.text)


class Article:
    def __init__(self, record: dict, issue: "CourierIssue"):
        self.article_metadata = record
        self.issue = issue

    @property
    def pages(self) -> Iterator[Page]:
        for page_number in self.article_metadata["pages"]:
            yield self.issue.get_page(page_number)

    @property
    def courier_id(self) -> str:
        return self.article_metadata["courier_id"]

    @property
    def record_number(self) -> str:
        return self.article_metadata["record_number"]

    @property
    def title(self) -> str:
        return self.article_metadata["catalogue_title"]

    @property
    def year(self) -> str:
        return self.article_metadata["year"]

    @property
    def publication_date(self) -> str:
        return self.article_metadata["publication_date"]


class CourierIssue:
    def __init__(self, courier_id: str):
        self.issue_index = CONFIG.article_index.loc[CONFIG.article_index["courier_id"] == courier_id]
        self.issue = read_xml(list(CONFIG.pdfbox_xml_dir.glob(f'{courier_id}*.xml'))[0])
        self.double_pages = CONFIG.double_pages.get(courier_id, [])

    @property
    def articles(self) -> Iterator[Article]:
        with warnings.catch_warnings():
            warnings.simplefilter(action='ignore', category=FutureWarning)
            for record in self.issue_index.to_dict("record"):
                yield Article(record, self)

    @property
    def num_articles(self) -> int:
        return len(self.issue_index)

    @property
    def num_pages(self) -> int:
        return len(self.issue.document.page)

    def get_page(self, page_number: int) -> Page:
        page_delta = len([x for x in self.double_pages if x < page_number])
        pages = [p for p in self.issue.document.page if p["number"] == str(page_number - page_delta)]
        return Page(page_number, pages[0].cdata if len(pages) > 0 else "")

    def find_pattern(self, pattern: str) -> List[Tuple[int, int]]:
        page_numbers = []
        for i, page in enumerate(self.issue.document.page, 1):
            m = re.search(pattern, page.cdata, re.IGNORECASE)
            if m:
                page_numbers.append((i, page["number"]))
        return page_numbers
