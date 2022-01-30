import os
from pathlib import Path


FILES = Path(__file__).parent / 'files'
FILE = FILES / 'settings.json'
SIZE = os.stat(FILE).st_size
CONTENT = open(FILE, 'rb').read()
PARENT_ID = 1000


class Item:
    def __init__(self, type, id, name):
        self.type = type
        self.id = self._object_id = id
        self.name = name

    def _assert(self, type, id, name):
        assert self.type == type
        assert self.id == id
        assert self.name == name

    def __str__(self):
        return '%s %d %s' % (self.type.title(), self.id, self.name)
