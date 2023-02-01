from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

from courier.config import get_config
from courier.utils import flatten

from .elements import CourierIssue

CONFIG = get_config()


@dataclass
class IssueStatistics:
    issue: CourierIssue

    total_pages: int = field(init=False)
    assigned_pages: int = field(init=False)
    consolidated_pages: int = field(init=False)
    expected_article_pages: int = field(init=False)
    number_of_articles: int = field(init=False)
    year: int = field(init=False)
    missing_pages: List[Tuple[str, int, int]] = field(init=False)
    num_missing_pages: int = field(init=False)
    errors: List[Dict[str, Any]] = field(init=False)
    num_errors: int = field(init=False)

    def __post_init__(self) -> None:
        self.total_pages: int = len(self.issue)
        self.assigned_pages: int = len(self.issue.get_assigned_pages())
        self.consolidated_pages: int = len(self.issue.get_consolidated_pages())
        self.expected_article_pages: int = len(self.issue.get_article_pages())
        self.number_of_articles: int = self.issue.num_articles
        self.year: int = CONFIG.issue_index.loc[int(self.issue.courier_id.lstrip('0'))].year
        self.missing_pages: List[Tuple[str, int, int]] = [
            (x.courier_id or '', x.record_number or 0, len(x.pages) - len(x.texts)) for x in self.issue.articles
        ]
        self.num_missing_pages: int = sum(
            [len(x.pages) - len(x.texts) for x in self.issue.articles]
        )  # FIXME: Should return (expected - consolidated) instead? Rename?
        self.errors: List[Dict[str, Any]] = flatten(
            [[error.asdict for error in page.errors] for page in self.issue.pages if len(page.errors) != 0]
        )
        self.num_errors: int = len(self.errors)


if __name__ == '__main__':
    pass
