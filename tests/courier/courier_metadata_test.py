import pytest

# from courier.courier_metadata import create_article_index, extract_courier_id, expand_article_pages, create_article_index
import courier.courier_metadata as metadata


@pytest.mark.parametrize(
    "test_input_host_item, expected",
    [
        ('English title first eng|Other Title|eng keyword in wrong place', 'English title first eng'),
        ('Non-english title|English title not first eng|Another non-english title', 'English title not first eng'),
        ('No english title', None),
    ],
)
def test_extract_english_host_item_returns_expected_values(test_input_host_item, expected):
    result = metadata.extract_english_host_item(test_input_host_item)
    assert result == expected


def test_extract_english_host_with_multiple_valid_host_items_raises_value_error():
    with pytest.raises(ValueError, match="duplicate.*'First eng', 'Second eng'"):
        metadata.extract_english_host_item("First eng|Second eng")


@pytest.mark.parametrize(
    "test_input_eng_host_item, expected",
    [
        ('Fill zeroes 123 eng', '000123'),
        ('Text before 77050 eng', '077050'),
        ('No matching ID eng', None),
    ],
)
def test_extract_courier_id(test_input_eng_host_item, expected):
    result = metadata.extract_courier_id(test_input_eng_host_item)
    assert result == expected
    assert len(result) == 6


def test_extract_courier_id_with_invalid_input_raises_value_error():
    with pytest.raises(ValueError):  # , match="must be <= 6"):
        metadata.extract_courier_id('Title 1234567 eng')


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
def test_expand_article_pages(test_input_page_refs, expected):
    result = metadata.expand_article_pages(test_input_page_refs)
    assert result == expected


@pytest.mark.skip(reason="TODO")
def test_create_article_index():
    pass
