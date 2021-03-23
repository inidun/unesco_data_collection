from typing import Iterator, Tuple, List
import pandas as pd
import untangle
import re


class Page:
    def __init__(self, page_number: int, text: str):
        self.page_number = page_number
        self.text = text


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
    def __init__(self, issue_index: pd.DataFrame, issue: untangle.Element):
        self.issue_index = issue_index
        self.issue = issue

    @property
    def articles(self) -> Iterator[Article]:
        for record in self.issue_index.to_dict("record"):
            yield Article(record, self)

    def get_page(self, page_number: int) -> Page:
        pages = [p for p in self.issue.document.page if p["number"] == str(page_number)]
        return Page(page_number, pages[0].cdata if len(pages) > 0 else "")

    def find_pattern(self, pattern: str) -> List[Tuple]:

        page_numbers = []
        for i, page in enumerate(self.issue.document.page, 1):
            m = re.search(pattern, page.cdata, re.IGNORECASE)
            if m:
                page_numbers.append((i, page["number"]))

        return page_numbers