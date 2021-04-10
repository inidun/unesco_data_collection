import pytest

import courier.metadata as metadata


@pytest.mark.parametrize(
    "test_input_host_item, expected",
    [
        ('English title first eng|Other Title|eng keyword in wrong place', 'English title first eng'),
        ('Non-english title|English title not first eng|Another non-english title', 'English title not first eng'),
        ('No english title', None),
    ],
)
def test_get_english_host_item_returns_expected_values(test_input_host_item, expected):
    result = metadata.get_english_host_item(test_input_host_item)
    assert result == expected


def test_get_english_host_with_multiple_valid_host_items_raises_value_error():
    with pytest.raises(ValueError, match="duplicate.*'First eng', 'Second eng'"):
        metadata.get_english_host_item("First eng|Second eng")


@pytest.mark.parametrize(
    "test_input_eng_host_item, expected",
    [
        ('Fill zeroes 123 eng', '000123'),
        ('Text before 77050 eng', '077050'),
    ],
)
def test_get_courier_id_returns_expected_values(test_input_eng_host_item, expected):
    result = metadata.get_courier_id(test_input_eng_host_item)
    assert result == expected
    assert len(result) == 6


def test_get_courier_id_with_missing_id_returns_none():
    assert metadata.get_courier_id('No matching ID eng') is None


def test_get_courier_id_with_invalid_id_raises_value_error():
    with pytest.raises(ValueError):  # , match="must be <= 6"):
        metadata.get_courier_id('Title 1234567 eng')


@pytest.mark.parametrize(
    "test_input_page_refs, expected",
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
def test_get_expanded_article_pages_returns_exptected_values(test_input_page_refs, expected):
    result = metadata.get_expanded_article_pages(test_input_page_refs)
    assert result == expected


@pytest.mark.skip(reason="TODO")
def test_get_article_index():
    pass
