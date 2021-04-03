import re
from typing import Iterator, List, Tuple

import pandas as pd
import untangle


class Page:
    def __init__(self, page_number: int, text: str):
        self.page_number = page_number
        self.text = text

    def __repr__(self):
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
    def __init__(self, issue_index: pd.DataFrame, issue: untangle.Element, double_pages: List[int]):
        self.issue_index = issue_index
        self.issue = issue
        # FIXME: get double_pages from config
        self.double_pages = double_pages

    @property
    def articles(self) -> Iterator[Article]:
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

    def find_pattern(self, pattern: str) -> List[Tuple]:
        page_numbers = []
        for i, page in enumerate(self.issue.document.page, 1):
            m = re.search(pattern, page.cdata, re.IGNORECASE)
            if m:
                page_numbers.append((i, page["number"]))
        return page_numbers
