import pytest

from courier.courier_metadata import expand_article_pages


@pytest.mark.parametrize(
    "test_input, expected",
    [
        ('p. 1-2', [1, 2]),
        ('p. 1', [1]),
        ('p. 1, 2 ', [1, 2]),
        ('p. 1, 2-4 ', [1, 2, 3, 4]),
        ('p.1-2', [1, 2]),
        ('p.1', [1]),
        ('p. 1-2, 4 ', [1, 2, 4]),
        ('page 1', [1]),
        ('p., 1-2', [1, 2]),
        ('p. 1-2, 4-5 ', [1, 2, 4, 5]),
    ],
)
def test_expand_article_pages(test_input, expected):
    result = expand_article_pages(test_input)
    assert result == expected


def test_extract_courier_id():
    pass
