from loguru import logger


def test_loguru_fixture_works(caplog):
    logger.warning('Oh no!')
    assert 'Oh no!' in caplog.text
