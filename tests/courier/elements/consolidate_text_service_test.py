import pytest

from courier.elements import AssignPageService, ConsolidateTextService, CourierIssue, IssueStatistics
from courier.elements.consolidate_text_service import fuzzy_find_title


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
        pytest.param('033144', 14, None, 'Two decades in the world of science', True, '2 articles: Unable to find title (1st article).', marks=pytest.mark.skip('Incomplete')),
        pytest.param('033144', 14, None, 'New outposts of science', True, '2 articles: Unable to find title (2nd article).', marks=pytest.mark.skip('Incomplete')),

        # TODO: #45 Handle case: `Two articles starting on same page`
        pytest.param('062404', 26, 62420, 'UNESCO art pocket books: a new venture in art publishing', True, '2 articles: Starting on same page', marks=pytest.mark.skip('Incomplete')),
        pytest.param('062404', 26, 62421, 'UNESCO in retrospect and perspective', True, '2 articles: Starting on same page', marks=pytest.mark.skip('Incomplete')),

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


@pytest.mark.skip('Incomplete.')
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
        # (
        #     'Messages from space with solar batteries',
        #     [(1958, 'MESS AGES FROM SPACE WITH SOLAR JS A«, JL JL Its j JL £a kl)]')],
        #     (1958, 'MESS AGES FROM SPACE WITH SOLAR JS A«, JL JL Its j JL £a kl)]'),
        # ),
    ],
)
def test_fuzzy_find_title(title, candidate_titles, expected):
    result = fuzzy_find_title(title, candidate_titles)
    assert result == expected
