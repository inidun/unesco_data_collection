from courier.compile_issues import compile_issues, jinja_env, join_pages, read


def test_read_returns_text(tmp_path):
    test_file = tmp_path / 'test.txt'
    test_file.write_text('text')
    assert read(test_file) == 'text'
    assert len(list(tmp_path.iterdir())) == 1


# TODO: Parametrize
def test_join_pages(tmp_path):

    (tmp_path / 'test1.txt').write_text('page one')
    (tmp_path / 'test2.txt').write_text('page two')
    (tmp_path / 'test3.not_txt').write_text('page three')
    (tmp_path / 'not_basename.txt').write_text('page four')
    template = jinja_env.get_template('courier_issue.xml.jinja')

    assert len(list(tmp_path.iterdir())) == 4
    assert join_pages('test', tmp_path) == '\n--- 1 ---\npage one\n--- 2 ---\npage two'
    assert (
        join_pages('test', tmp_path, template)
        == '<?xml version="1.0" encoding="UTF-8"?>\n<document id="test">\n<page number="1">\n<![CDATA[\npage one\n]]>\n</page>\n<page number="2">\n<![CDATA[\npage two\n]]>\n</page>\n</document>'
    )


# TODO: Parametrize
def test_compile_issues(tmp_path):

    (tmp_path / 'test1.txt').write_text('page one')
    (tmp_path / 'test2.txt').write_text('page two')
    template = jinja_env.get_template('courier_issue.xml.jinja')

    compile_issues(['test'], tmp_path, tmp_path / 'output')
    assert read(tmp_path / 'output/test.xml') == '\n--- 1 ---\npage one\n--- 2 ---\npage two'

    compile_issues(['test'], tmp_path, tmp_path / 'output', template=template)
    assert (
        read(tmp_path / 'output/test.xml')
        == '<?xml version="1.0" encoding="UTF-8"?>\n<document id="test">\n<page number="1">\n<![CDATA[\npage one\n]]>\n</page>\n<page number="2">\n<![CDATA[\npage two\n]]>\n</page>\n</document>'
    )
