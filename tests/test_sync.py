from tempfile import NamedTemporaryFile
from unittest import mock
from os import getcwd
from pathlib import Path

from bsync.sync import BoxSync

from .base import Item, FILES, FILE, LOGGER


def test_cwd():
    api = mock.MagicMock()
    sync = BoxSync(api, LOGGER, 111, '.')
    assert sync.glob == '*'
    assert sync.source_folder.absolute() == Path(getcwd())


def test_sync():
    api = mock.MagicMock()
    sync = BoxSync(api, LOGGER, 111, f'{FILES}::*')
    assert sync.glob == '*'
    assert sync.source_folder.absolute() == FILES.absolute()

    parent_folder = Item('folder', 111, 'box folder')
    api.client.folder.return_value.get.return_value = parent_folder
    mocked_item = mock.MagicMock()
    mocked_item.__getitem__.return_value = 'foobar.py'
    mocked_item.get.return_value.path_collection = {'entries': [
        Item('folder', 0, 'all files'),
        parent_folder,
        Item('folder', 222, 'subfolder')
    ]}
    mocked_item2 = mock.MagicMock()
    mocked_item2.__getitem__.return_value = 'settings.json'
    mocked_item2._object_id = 777
    mocked_item2.get.return_value.path_collection = {'entries': [
        Item('folder', 0, 'all files'),
        parent_folder,
    ]}
    api.client.folder.return_value.get_items.return_value = [mocked_item, mocked_item2]
    box_paths = list(sync.get_box_paths())
    assert len(box_paths) == 2
    path, item = box_paths[0]
    assert item == mocked_item
    assert path == FILES / 'subfolder' / 'foobar.py'
    assert len(api.client.folder.call_args_list) == 2

    sync.run()
    api.upload.assert_called()
    args, _ = api.create_folder.call_args_list[0]
    assert args == (111, 'subfolder')
    args, _ = api.update.call_args_list[0]
    assert args == (777, FILE)

    with NamedTemporaryFile() as outfile:
        sync.output(outfile.name)
        assert len(open(outfile.name).readlines()) == 4
