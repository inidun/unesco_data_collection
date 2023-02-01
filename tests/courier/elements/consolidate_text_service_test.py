from typing import List, Tuple

import pytest
from thefuzz import process

from courier.config import get_config
from courier.elements import AssignPageService, ConsolidateTextService, CourierIssue, IssueStatistics
from courier.elements.consolidate_text_service import (
    bow,
    candidate_bow_equals_title_bow,
    common_words_equals_candidate_bow,
    common_words_half_or_more,
    common_words_three_or_more,
    evaluate_functions,
    get_best_candidate,
    title_is_one_word_and_candidate_contains_same_word,
    two_first_words_equal,
)


def test_issue_has_no_consolidated_pages_as_default():
    issue = CourierIssue('012656')
    assert IssueStatistics(issue).consolidated_pages == 0


@pytest.mark.parametrize(
    # fmt: off
    'issue_number, page_number, record_number, article_title, expected, comment',
    [
        # Base case
        ('062404', 27, 62421, 'UNESCO in retrospect and perspective', True, 'Base case: only one article on page'),

        # TODO: #43, #44 Handle cases: `Unable to find title on page (1st)` and `Unable to find title on page (2nd)`
        # NOTE: `pdfextract` does NOT find any candidates on page 14 in issue 033144. Test other page.
        ('033144', 14, None, 'Two decades in the world of science', False, '2 articles: Unable to find title (1st article).'),
        ('033144', 14, None, 'New outposts of science', False, '2 articles: Unable to find title (2nd article).'),

        # TODO: #45 Handle case: `Two articles starting on same page`
        ('062404', 26, 62420, 'UNESCO art pocket books: a new venture in art publishing', True, '2 articles: Starting on same page'),
        ('062404', 26, 62421, 'UNESCO in retrospect and perspective', True, '2 articles: Starting on same page'),

        # Unhandled
        ('063436', 23, 63295, 'Index of prosperity: S.T.P. (scientific and technical potential)', False, '2 articles: None of them starts on page. (19,20,21,22,23)'),
        ('063436', 23, 63435, 'UNESCO expands its science programme', False, '2 articles: None of them starts on page. (22,23)'),
        ('073938', 7, 73939, 'The Internationalist', False, 'More than two articles on page.'),
    ],
    # fmt: on
)
def test_ConsolidateArticleTexts(issue_number, page_number, record_number, article_title, expected, comment):
    issue = CourierIssue(issue_number)
    AssignPageService().assign(issue)

    if record_number is not None:
        article = issue.get_article(record_number)  # type: ignore
    else:
        article = issue.get_article_from_title(article_title)  # type: ignore
    assert article is not None

    page = issue.get_page(page_number)

    service = ConsolidateTextService()
    service._assign_segment(article, page, min_second_article_position=0)  # pylint: disable=protected-access

    result = any(x for x in article.texts if x[0] == page_number)
    assert result == expected, comment


# TODO: Test for offset. Edit in pdfextract
# print(A1.texts[0][1])
# print(A2.texts[0][1])
@pytest.mark.skip('Incomplete.')
def test_assign_segments_to_articles_case_A1_and_A2_starts_on_page():
    issue = CourierIssue('068778')
    AssignPageService().assign(issue)
    ConsolidateTextService().consolidate(issue)
    A1 = issue.get_article(189520)
    A2 = issue.get_article(68780)

    # TODO: Test if offset error
    assert A1 is not None
    assert A2 is not None


# @pytest.mark.skip('Incomplete.')
def test_cosolidated_pages():
    issue = CourierIssue('012656')
    # issue = CourierIssue('068778')
    # issue = CourierIssue('073649')
    AssignPageService().assign(issue)
    ConsolidateTextService().consolidate(issue)

    assert IssueStatistics(issue).num_missing_pages == 0


# TODO: Add more tests
@pytest.mark.parametrize(
    'title, candidate_titles, expected',
    [
        (
            'Where the sky is black',
            [(0, 'WHERE THE SKY IS BLACK (Continued)')],
            (0, 'WHERE THE SKY IS BLACK (Continued)'),
        ),
        (
            'Treasures of world art',
            [(0, 'TREASURES\nOF\nWORLD ART O\nj Priestess of the springs\n')],
            (0, 'TREASURES\nOF\nWORLD ART O\nj Priestess of the springs\n'),
        ),
        (
            'India moves towards self-sufficency in food',
            [(2355, 'INDIA MOVES')],
            (2355, 'INDIA MOVES'),
        ),
        (
            'Messages from space with solar batteries',
            [(1958, 'MESS AGES FROM SPACE WITH SOLAR JS A«, JL JL Its j JL £a kl)]')],
            (1958, 'MESS AGES FROM SPACE WITH SOLAR JS A«, JL JL Its j JL £a kl)]'),
        ),
        (
            'Paris gets a new heart, a bold project is changing the appearance and cultural life of the French capital',
            [(39, '20'), (5551, 'Paris gets new heart by Nino Frank')],
            (5551, 'Paris gets new heart by Nino Frank'),
        ),
        (
            'A Pioneer of scientific observation',
            [(42, '16'), (3009, 'One night he dreamt that lie was'), (5313, 'pioneer scientific by Mohammed')],
            (None, None),
        ),
        (
            "The Woman we called 'la patronne'",
            [(34, '11'), (5150, 'THE WOM by Marguerite Perey'), (5784, 'June 1929, as shy')],
            (None, None),
        ),
        (
            "Citizen Paine: the turbulent life of a fiery revolutionary who proclaimed 'my country is the world'",
            [
                (0, 'Yet in an indirect way there was'),
                (2320, 'and peculiar forms. It is found in'),
                (4675, 'CITIZEN PAINE'),
                (5117, '28'),
            ],
            (4675, 'CITIZEN PAINE'),
        ),
    ],
)
def test_fuzzy_find_title(title, candidate_titles, expected):
    result = get_best_candidate(title, candidate_titles)
    assert result == expected


def get_page_titles(courier_id: str, page: int) -> List[Tuple[int, str]]:
    issue = CourierIssue(courier_id)
    AssignPageService().assign(issue)
    ConsolidateTextService().consolidate(issue)
    return issue.get_page(page).titles


def test_get_page_titles_returns_expected():
    courier_id = '078370'
    page = 22
    titles = get_page_titles(courier_id, page)
    assert titles == [(34, '11'), (5150, 'THE WOM by Marguerite Perey'), (5784, 'June 1929, as shy')]


def get_article_title(record_number: int) -> str:
    article_index = get_config().article_index
    return article_index[article_index['record_number'] == record_number].iloc[0].catalogue_title


def test_get_article_title():
    title = get_article_title(66288)
    assert title == 'Messages from space with solar batteries'


@pytest.mark.parametrize(
    'courier_id, record_number, page',
    [
        ('066285', 66288, 17),
        ('050399', 50404, 20),
        ('074808', 46517, 28),
        ('074817', 48081, 12),
        ('074642', 41135, 26),
        ('074642', 41135, 26),
        ('074758', 41073, 10),
        ('074686', 52513, 17),
        ('074686', 52554, 25),
        # ('074826', 49572, 28),
        # ('078370', 21124, 22),
        # ('074875', 50320, 16),
        # ('074686', 52575, 28),
        ('074816', 48053, 14),
        ('062404', 62420, 26),
        ('062404', 62421, 26),
    ],
)
def test_fuzzy_find_title_returns_title(courier_id, record_number, page):
    title = get_article_title(record_number)
    candidate_titles = get_page_titles(courier_id, page)
    _, result = get_best_candidate(title, candidate_titles)
    assert result is not None, title


@pytest.mark.parametrize(
    'courier_id, record_number, page',
    [
        ('066285', 66288, 17),
        ('050399', 50404, 20),
        ('074808', 46517, 28),
        ('074817', 48081, 12),
        ('074642', 41135, 26),
        ('074642', 41135, 26),
        ('074758', 41073, 10),
        ('074686', 52513, 17),
        ('074686', 52554, 25),
        ('074826', 49572, 28),
        ('078370', 21124, 22),
        ('074875', 50320, 16),
        ('074686', 52575, 28),
        ('074816', 48053, 14),
        ('066943', 66935, 27),
        ('068108', 68120, 11),
        ('076565', 76562, 38),
    ],
)
def test_fuzzywuzzy(courier_id, record_number, page):
    title = get_article_title(record_number)
    candidate_titles = get_page_titles(courier_id, page)
    _, result = process.extractOne(title, candidate_titles)[0]
    assert all(result), title


def test_bow_removes_special_characters():
    title = 'ONE two 23b ?= abc%'
    assert bow(title) == {'23b', 'abc', 'one', 'two'}


@pytest.mark.parametrize(
    'functions, args, expected',
    [
        ([lambda x, y: x + y, lambda x, y: x * y], (2, 3), [5, 6]),
        ([lambda x, y: x.lower() + y.upper(), lambda x, y: x.upper() + y.lower()], ('a', 'b'), ['aB', 'Ab']),
    ],
)
def test_evaluate_functions(functions, args, expected):
    result = evaluate_functions(functions, args)
    assert result == expected


@pytest.mark.parametrize(
    'title, candidate, expected',
    [
        ('These are equal', 'These are equal', 3),
        ('These are not', 'No', 0),
        ('', '', 0),
    ],
)
def test_candidate_bow_equals_title_bow(title, candidate, expected):
    result = candidate_bow_equals_title_bow(title, candidate)
    assert result == expected


@pytest.mark.parametrize(
    'title, candidate, expected',
    [
        ('one two three', 'one two three', 2),
        ('one two three', 'one two', 0),
        ('', '', 0),
    ],
)
def test_common_words_three_or_more(title, candidate, expected):
    result = common_words_three_or_more(title, candidate)
    assert result == expected


@pytest.mark.parametrize(
    'title, candidate, expected',
    [
        ('a b c d e', 'a b c', 1),
        ('a b c d e', 'a b', 0),
        ('a b c d', 'a b', 1),
        ('a b', 'a', 1),
    ],
)
def test_common_words_more_than_half(title, candidate, expected):
    result = common_words_half_or_more(title, candidate)
    assert result == expected


@pytest.mark.parametrize(
    'title, candidate, expected',
    [
        ('a b c d', 'a b c', 1),
        ('a b c d', 'a b', 1),
        ('a b c d', 'a b q', 0),
        ('a b c', 'd e f', 0),
        ('', '', 0),
    ],
)
def test_common_words_equals_candidate_bow(title, candidate, expected):
    result = common_words_equals_candidate_bow(title, candidate)
    assert result == expected


@pytest.mark.parametrize(
    'title, candidate, expected',
    [
        ('one two', 'one two three', 1),
        ('one two three', 'one two', 1),
        ('one three', 'one two', 0),
        ('', '', 0),
    ],
)
def test_two_first_words_equal(title, candidate, expected):
    result = two_first_words_equal(title, candidate)
    assert result == expected


@pytest.mark.parametrize(
    'title, candidate, expected',
    [
        ('oneword', 'oneword a b c', 1),
        ('oneword', 'a b c oneword', 1),
        ('oneword', 'a b c', 0),
        ('two words', 'two words a b c', 0),
    ],
)
def test_title_is_one_word_and_candidate_contains_same_word(title, candidate, expected):
    result = title_is_one_word_and_candidate_contains_same_word(title, candidate)
    assert result == expected
