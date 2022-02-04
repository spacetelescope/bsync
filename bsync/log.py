import logging


LEVELS = {name.lower(): value for name, value in logging._nameToLevel.items() if value}


def get_logger(log_level=None, log_file=None):
    """
    Configures a logger w/ file/stream handler from settings
    """
    level = LEVELS.get(log_level, logging.INFO)
    logger = logging.getLogger('bsync')
    logger.setLevel(level)
    handler = logging.FileHandler(log_file) if log_file else logging.StreamHandler()
    handler.setLevel(level)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
