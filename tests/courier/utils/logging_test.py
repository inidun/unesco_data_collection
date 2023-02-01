from pathlib import Path
from tempfile import TemporaryDirectory

from courier.utils.logging import file_logger


def test_file_logger():
    with TemporaryDirectory() as output_dir:
        logfile = Path(output_dir) / 'test.log'
        with file_logger(logfile, format='{message}') as logger:
            logger.info('yes')
        logger.info('no')
        with open(logfile, 'r', encoding='utf-8') as fp:
            content = fp.read()
        assert (Path(output_dir) / 'test.log').exists()
        assert content == 'yes\n'


def test_file_logger_wrapping():
    with TemporaryDirectory() as output_dir:
        logfile1 = Path(output_dir) / 'test1.log'
        logfile2 = Path(output_dir) / 'test2.log'
        logfile3 = Path(output_dir) / 'test3.log'

        with file_logger(logfile1, format='{message}') as logger1:
            logger1.info('1')
            with file_logger(logfile2, format='{message}') as logger2:
                logger1.info('12')
                logger2.info('2')
                with file_logger(logfile3, format='{message}') as logger3:
                    logger1.info('123')
                    logger2.info('23')
                    logger3.info('3')

        assert (Path(output_dir) / 'test1.log').exists()
        assert (Path(output_dir) / 'test2.log').exists()
        assert (Path(output_dir) / 'test3.log').exists()

        with open(logfile1, 'r', encoding='utf-8') as fp:
            assert fp.read() == '1\n12\n123\n'

        with open(logfile2, 'r', encoding='utf-8') as fp:
            assert fp.read() == '2\n23\n'

        with open(logfile3, 'r', encoding='utf-8') as fp:
            assert fp.read() == '3\n'
