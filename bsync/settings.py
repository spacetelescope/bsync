import logging


LOG_LEVELS = {name.lower(): value for name, value in logging._nameToLevel.items() if value}

# 20MB limit for simple uploads, after that, use chunked
BOX_UPLOAD_LIMIT = 2 * 10 ** 7

# PATHS seperator for identifying source paths by glob
PATH_SEP = '::'
