from dataclasses import dataclass
from typing import List, Tuple

from courier.config import get_config

from .elements import CourierIssue

CONFIG = get_config()


@dataclass
class IssueStatistics:

    issue: CourierIssue

    @property
    def total_pages(self) -> int:
        """Number of pages in issue"""
        return len(self.issue)

    @property
    def assigned_pages(self) -> int:
        """Number of pages in issue assigned to an article"""
        return len(self.issue.get_assigned_pages())

    @property
    def consolidated_pages(self) -> int:
        """Number of consolidated pages in issue"""
        return len(self.issue.get_consolidated_pages())

    @property
    def expected_article_pages(self) -> int:
        """Number of article pages in issue according to index"""
        return len(self.issue.get_article_pages())

    @property
    def number_of_articles(self) -> int:
        """Number of articles in issue"""
        return self.issue.num_articles

    @property
    def year(self) -> int:
        return CONFIG.issue_index.loc[int(self.issue.courier_id.lstrip('0'))].year

    @property
    def missing_pages(self) -> List[Tuple[str, int, int]]:
        return [(x.courier_id or '', x.record_number or 0, len(x.pages) - len(x.texts)) for x in self.issue.articles]

    @property
    def num_missing_pages(self) -> int:
        return sum([len(x.pages) - len(x.texts) for x in self.issue.articles])


if __name__ == '__main__':
    pass
