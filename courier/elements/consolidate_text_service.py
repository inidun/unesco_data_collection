import re

# NOTE: Main logic
from operator import itemgetter, methodcaller
from typing import Any, Callable, List, Optional, Set, Tuple

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
        return get_best_candidate(article.catalogue_title, titles)[0]


def bow(title: str) -> Set[str]:
    return set(re.sub(r'\W+', ' ', title).lower().split())


def evaluate_functions(functions: List[Callable[[Any, Any], int]], args: Tuple[Any, Any]) -> List[int]:
    """Evaluates list of functions using the same arguments and returns the return values of the functions as a list

    Args:
        functions (List[Callable[[Any, Any], int]]): List of functions to be evaluated
        args (Tuple[Any, Any]): Arguments to pass to the functions

    Returns:
        List[int]: List of return values
    """
    return list(map(methodcaller('__call__', *args), functions))


def candidate_bow_equals_title_bow(title: str, candidate_title: str) -> int:
    return 3 if len(bow(candidate_title)) > 0 and bow(candidate_title) == bow(title) else 0


def common_words_three_or_more(title: str, candidate_title: str) -> int:
    common_words = bow(title).intersection(bow(candidate_title))
    return 2 if len(common_words) >= 3 else 0


# TODO: #57 Evaluate if overmatches
# now:          |C| > 0 and |C∩T| >= |T|/2
# change to:    C∩T >= 2 and C∩T >= |T|/2
def common_words_more_than_half(title: str, candidate_title: str) -> int:
    common_words = bow(title).intersection(bow(candidate_title))
    return 1 if len(bow(candidate_title)) > 0 and len(common_words) >= len(bow(title)) / 2 else 0


def common_words_equals_candidate_bow(title: str, candidate_title: str) -> int:
    common_words = bow(title).intersection(bow(candidate_title))
    return 1 if len(bow(candidate_title)) > 0 and common_words == bow(candidate_title) else 0


def two_first_words_equal(title: str, candidate_title: str) -> int:
    if len(bow(candidate_title)) == 0 or len(bow(title)) == 0:
        return 0
    return 1 if candidate_title.lower().split()[:2] == title.lower().split()[:2] else 0


def title_is_one_word_and_candidate_contains_same_word(title: str, candidate_title: str) -> int:
    common_words = bow(title).intersection(bow(candidate_title))
    return 1 if len(bow(title)) == 1 and common_words == bow(title) else 0


def get_best_candidate(
    title: str, title_candidates: List[Tuple[int, str]], functions: List[Callable[[str, str], int]] = None
) -> Tuple[Optional[int], Optional[str]]:
    """Returns the candidate from a list of title candidates best matching title

    If there is only one candidate and the first two words in candidate and title are the same, candidate is returned.
    If there is more than one candidate, the candidate with the highest score efter being evaluated using the following (weighted) rules is selected:

        - |C| > 0 and C = T
        - C∩T >= 3
        - C∩T >= 2 and C∩T >= |T|/2
        - |C| > 0 and C∩T = C
        - First two words in c and t are equal
        - |T| = 1 and C∩T = T

    Where T is the set of tokens in title t, C is the set of tokens in candidate c, and C∩T is the set of common tokens in C and T.

    Args:
        title (str): The title
        candidate_titles (List): A list of title candidates

    Returns:
        Tuple[Optional[int], Optional[str]]: Tuple containing the position of, and the string of the best matching candidate
    """

    if title is None:
        return (None, None)

    if len(title_candidates) == 1:
        position, candidate_title = title_candidates[0]
        if candidate_title.lower().split()[:2] == title.lower().split()[:2]:
            return (position, candidate_title)

    functions: List[Callable[[str, str], int]] = (
        functions
        if functions is not None
        else [
            candidate_bow_equals_title_bow,
            common_words_three_or_more,
            common_words_more_than_half,
            common_words_equals_candidate_bow,
            two_first_words_equal,
            title_is_one_word_and_candidate_contains_same_word,
        ]
    )

    candidate, score = max(
        [((p, c), evaluate_functions(functions, (title, c))) for p, c in title_candidates],
        key=itemgetter(1),
        default=((None, None), [0]),
    )
    return candidate if sum(score) > 0 else (None, None)


if __name__ == '__main__':
    pass
