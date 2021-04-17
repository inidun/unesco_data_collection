from courier.split_article_pages import create_regexp


def test_create_regexp():
    title = 'A nice and happy! title.? 77Maybe#'
    expr = create_regexp(title)
    assert isinstance(expr, str)
    assert expr == '[^a-zåäö]+nice[^a-zåäö]+and[^a-zåäö]+happy[^a-zåäö]+title[^a-zåäö]+maybe'
