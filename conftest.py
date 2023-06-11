import sys
import logging

def pytest_configure(config):
    sys._pytest_mode = True
    # configure basic logging, with file name and line number, debug level
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s',
        level=logging.DEBUG)


def pytest_unconfigure(config):
    del sys._pytest_mode