from typing import List, Optional, Set, Tuple

from .elements import Article, CourierIssue, ExtractionError, Page


# FIXME: Rename 'AddTextToArticles'?
class ConsolidateTextService:
    def consolidate(self, issue: CourierIssue, min_second_article_position: int = 80) -> None:
        for article in issue.articles:
            for page in article.pages:
                self._assign_segment(article, page, min_second_article_position)

    def _assign_segment(self, article: Article, page: Page, min_second_article_position: int = 80) -> None:

        if page.number_of_articles == 1:
            article.texts.append((page.page_number, page.text))

        elif page.number_of_articles == 2:
            """Find break position and which part belongs to which article"""
            A1: Article = article
            A2: Article = page.articles[1] if page.articles[1] is not article else page.articles[0]

            # Case 1: Article 1 starts before current page, Article 2 starts on current page
            # TODO: #43 Handle case: `Unable to find title on page (1st)`
            if A1.min_page_number < page.page_number and A2.min_page_number == page.page_number:
                """Assumption: Article 1 is at the beginning of the page. Find Article 2's title"""

                position = self.find_matching_title_position(A2, page.titles)
                if position is not None:
                    A1.texts.append((page.page_number, page.text[:position]))
                else:
                    article.errors.append(
                        f'Unhandled case: Page {page.page_number}. 2 articles: Unable to find title (1st article).'
                    )
                    article.errors.append(f'\nTitles on page {page.page_number}:\n{page.get_pritty_titles()}')
                    page.errors.append(ExtractionError(article, page.page_number, 1, page.get_pritty_titles()))

            # Case 2: Article 2 starts before current page, Article 1 starts on current page
            # TODO: #44 Handle case: `Unable to find title on page (2nd)`
            elif A2.min_page_number < page.page_number and A1.min_page_number == page.page_number:
                """A1 ligger sist på sidan: => Hitta A1's titel"""
                position = self.find_matching_title_position(A1, page.titles)
                if position is not None:
                    A1.texts.append((page.page_number, page.text[position:]))
                else:
                    article.errors.append(
                        f'Unhandled case: Page {page.page_number}. 2 articles: Unable to find title (2nd article).'
                    )
                    article.errors.append(f'\nTitles on page {page.page_number}:\n{page.get_pritty_titles()}')
                    page.errors.append(ExtractionError(article, page.page_number, 2, page.get_pritty_titles()))

            # Case 3: Article 1 and Article 2 both start on current page
            # TODO: #45 Handle case: `Two articles starting on same page`
            elif A1.min_page_number == A2.min_page_number == page.page_number:
                position_A1 = self.find_matching_title_position(A1, page.titles)
                position_A2 = self.find_matching_title_position(A2, page.titles)

                if position_A1 is not None and position_A2 is not None:
                    if position_A1 < position_A2:
                        A1.texts.append((page.page_number, page.text[:position_A2]))
                    else:
                        A1.texts.append((page.page_number, page.text[position_A1:]))
                elif position_A1 is not None and position_A1 > min_second_article_position:
                    A1.texts.append((page.page_number, page.text[position_A1:]))
                elif position_A2 is not None and position_A2 > min_second_article_position:
                    A1.texts.append((page.page_number, page.text[:position_A2]))
                else:
                    article.errors.append(
                        f'Unhandled case: Page {page.page_number}. 2 articles: Starting on same page.'
                    )
                    page.errors.append(ExtractionError(article, page.page_number, 3))

            # Case 4: Neither Article 1 or Article 2 start on current page
            else:
                article.errors.append(
                    f'Unhandled case: Page {page.page_number}. 2 articles: None of them starts on page.'
                )
                page.errors.append(ExtractionError(article, page.page_number, 4))

        # Case 5: Current page contains more than 2 articles
        else:
            article.errors.append(f'Unhandled case: Page {page.page_number}. More than two articles on page.')
            page.errors.append(ExtractionError(article, page.page_number, 5))

    def find_matching_title_position(self, article: Article, titles: List) -> Optional[int]:
        return fuzzy_find_title(article.catalogue_title, titles)[0]


# NOTE: Main logic
def fuzzy_find_title(title: str, titles: List) -> Tuple[Optional[int], Optional[str]]:
    if title is None:
        return (None, None)
    title_bow: Set[str] = set(title.lower().split())
    for position, candidate_title in titles:
        candidate_title_bow: Set[str] = set(candidate_title.lower().split())
        common_words = title_bow.intersection(candidate_title_bow)
        if len(common_words) >= 2 and len(common_words) >= len(title_bow) / 2:
            return position, candidate_title
    return (None, None)


if __name__ == '__main__':
    pass
