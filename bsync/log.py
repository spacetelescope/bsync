import logging


LEVELS = {name.lower(): value for name, value in logging._nameToLevel.items() if value}


def get_logger(options):
    level = LEVELS.get(options['log_level'] or 'info')
    logger = logging.getLogger('bsync')
    logger.setLevel(level)
    handler = logging.FileHandler(options['log_file']) if options['log_file'] else logging.StreamHandler()
    handler.setLevel(level)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
