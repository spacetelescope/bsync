from unittest import mock
from pathlib import Path
from getpass import getuser

from click.testing import CliRunner

from .base import FILES, FILE


@mock.patch('bsync.sync.BoxSync')
@mock.patch('bsync.log.get_logger')
@mock.patch('bsync.api.BoxAPI')
def test_bsync(mocked_api, mocked_logger, mocked_sync):
    from bsync.cli import bsync

    runner = CliRunner()
    result = runner.invoke(bsync, [f'{FILES}:*.json', '1234', f'--settings={FILE}', '--output=bar.log'])
    assert result.exit_code == 0
    options = {
        'source_folder_paths': Path(f'{FILES}:*.json'),
        'box_folder_id': 1234,
        'box_user': getuser(),
        'settings': FILE,
        'ipdb': False,
        'log_level': None,
        'log_file': None,
        'output': Path('bar.log')
    }
    args, _ = mocked_api.call_args_list[0]
    assert args[0] == options
