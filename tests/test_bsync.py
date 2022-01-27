import logging
import sys

from bsync.api import BoxAPI
from bsync.cli import bsync
from bsync.log import get_logger
from bsync.sync import BoxSync


def test_logger():
    logger = get_logger({})
    assert logger.level == logging.INFO
    assert len(logger.handlers) == 1
    assert logger.handlers[0].level == logging.INFO
    assert logger.handlers[0].stream == sys.stderr
