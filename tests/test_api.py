import logging
import sys

from unittest import mock


from .base import Item, SIZE, FILE, PARENT_ID, CONTENT, LOGGER


class MockedStat:
    st_size = 2 * 10 ** 7


class MockedSession:
    total_parts = 10
    part_size = SIZE
    upload_part_bytes = mock.MagicMock()
    commit = mock.MagicMock()
    commit.return_value = Item('file', 333, 'chunked file')


def test_logger():
    assert LOGGER.level == logging.INFO
    assert len(LOGGER.handlers) == 1
    hdlr = LOGGER.handlers[0]
    assert hdlr.level == logging.INFO
    assert hdlr.stream == sys.stderr


@mock.patch('boxsdk.Client')
@mock.patch('boxsdk.JWTAuth')
def test_api(mocked_jwt, mocked_client):
    from bsync.api import BoxAPI

    mocked_client.return_value.users.return_value = [1]
    api = BoxAPI(LOGGER, 'me',  FILE)

    mocked_folder = mocked_client.return_value.as_user.return_value.folder
    mocked_file = mocked_client.return_value.as_user.return_value.file
    mocked_folder.return_value.create_subfolder.return_value = Item('folder', 111, 'test subfolder')
    subfolder = api.create_folder(PARENT_ID, 'test-folder')
    subfolder._assert('folder', 111, 'test subfolder')
    api.client.folder.assert_called_once_with(PARENT_ID)
    mocked_jwt.assert_called_once_with('id', 'secret', 'enterprise', 'public',
                                       rsa_private_key_data='private', rsa_private_key_passphrase='passphrase')

    mocked_folder.return_value.upload.return_value = Item('file', 222, 'test file')
    newfile = api.upload(PARENT_ID, FILE)
    assert api.client.folder.call_count == 2
    newfile._assert('file', 222, 'test file')

    with mock.patch('os.stat') as mocked_stat:
        mocked_stat.return_value = stat = MockedStat()
        mocked_folder.return_value.create_upload_session.return_value = session = MockedSession()
        newfile = api.upload(PARENT_ID, FILE)
        assert session.total_parts == len(session.upload_part_bytes.call_args_list)
        args, _ = session.upload_part_bytes.call_args_list[0]
        assert args == (CONTENT, 0, stat.st_size)
        args, _ = session.upload_part_bytes.call_args_list[1]
        assert args == (b'', SIZE, stat.st_size)
        session.commit.assert_called()
        newfile._assert('file', 333, 'chunked file')

    mocked_file.return_value.update_contents.return_value = Item('file', 444, 'test update')
    newfile = api.update(444, FILE)
    assert api.client.folder.call_count == 3
    assert api.client.file.call_count == 1
    newfile._assert('file', 444, 'test update')
