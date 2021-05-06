import pytest
from jinja2 import Template

from courier.compile_issues import IssueCompiler, jinja_env, join_pages, read


def test_read_returns_text(tmp_path):
    test_file = tmp_path / 'test.txt'
    test_file.write_text('text')
    assert read(test_file) == 'text'
    assert len(list(tmp_path.iterdir())) == 1


@pytest.mark.parametrize(
    'basename, template, expected',
    [
        ('test', None, '\n--- 1 ---\npage one\n--- 2 ---\npage two'),
        (
            'test',
            jinja_env.get_template('courier_issue.xml.jinja'),
            '<?xml version="1.0" encoding="UTF-8"?>\n<document id="test">\n<page number="1">\n<![CDATA[\npage one\n]]>\n</page>\n<page number="2">\n<![CDATA[\npage two\n]]>\n</page>\n</document>',
        ),
    ],
)
def test_join_pages(basename, template, expected, tmp_path):

    (tmp_path / 'test1.txt').write_text('page one')
    (tmp_path / 'test2.txt').write_text('page two')
    (tmp_path / 'test3.not_txt').write_text('page three')
    (tmp_path / 'not_basename.txt').write_text('page four')
    assert len(list(tmp_path.iterdir())) == 4

    result = join_pages(basename, tmp_path, template)
    assert result == expected


@pytest.mark.parametrize(
    'template, expected',
    [
        (
            Template('{% for page in pages %}\n--- {{ loop.index }} ---\n{{ page|trim }}{% endfor %}'),
            '\n--- 1 ---\npage one\n--- 2 ---\npage two',
        ),
        (
            'courier_issue.xml',
            '<?xml version="1.0" encoding="UTF-8"?>\n<document id="test">\n<page number="1">\n<![CDATA[\npage one\n]]>\n</page>\n<page number="2">\n<![CDATA[\npage two\n]]>\n</page>\n</document>',
        ),
    ],
)
def test_compile_issues(template, expected, tmp_path):

    (tmp_path / 'test1.txt').write_text('page one')
    (tmp_path / 'test2.txt').write_text('page two')

    IssueCompiler(template).compile_issues(['test'], tmp_path, tmp_path / 'output')
    result = read(tmp_path / 'output/test.xml')
    assert result == expected
