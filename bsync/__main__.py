import sys

from bsync.cli import bsync


if __name__ == '__main__':
    bsync.main(sys.argv[1:], standalone_mode=False)
