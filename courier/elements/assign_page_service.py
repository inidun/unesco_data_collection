import warnings
from typing import List

from .elements import Article, CourierIssue, Page


class AssignPageService:
    def assign(self, issue: CourierIssue) -> None:
        if issue.get_assigned_pages():
            warnings.warn(f'Pages already assigned to {issue.courier_id}', stacklevel=2)
            return
        for page in issue.pages:
            articles: List[Article] = self._find_articles_on_page(issue, page)
            page.articles = articles
            for article in articles:
                article.pages.append(page)

    def _find_articles_on_page(self, issue: CourierIssue, page: Page) -> List[Article]:
        articles = [
            a for a in issue.articles if page.page_number in a.page_numbers
        ]  # FIXME: Handle that a.page_numbers can be None
        return articles


if __name__ == '__main__':
    pass
