from courier.scripts.tagged_issue_to_articles import get_issue_articles


def test_get_issue_articles_returns_expected():

    filename = 'tests/fixtures/courier/tagged_issue/tagged_1234_123456.md'

    articles = get_issue_articles(filename)

    assert len(articles) == 2
    assert '78910' in articles.keys()
