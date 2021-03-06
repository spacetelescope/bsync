from unittest import mock
from pathlib import Path

from click.testing import CliRunner

from .base import FILES, FILE


@mock.patch('bsync.sync.BoxSync')
@mock.patch('bsync.log.get_logger')
@mock.patch('bsync.api.BoxAPI')
def test_bsync(mocked_api, mocked_logger, mocked_sync):
    from bsync.cli import bsync

    runner = CliRunner()
    result = runner.invoke(bsync, f'{FILES}:*.json 1234 --settings={FILE} --output=foo.csv -l error --log-file bar.log -c 2')
    assert result.exit_code == 0
    args, _ = mocked_logger.call_args_list[0]
    assert args == ('error', Path('bar.log'))
    args, _ = mocked_api.call_args_list[0]
    assert args == (mocked_logger(), FILE)
    args, _ = mocked_sync.call_args_list[0]
    assert args == (mocked_api(), mocked_logger(), 2, 1234, f'{FILES}:*.json')
    args, _ = mocked_sync.return_value.output.call_args_list[0]
    assert args[0] == Path('foo.csv')


def test_version():
    from bsync.__version__ import __version__
    from bsync.cli import bsync

    runner = CliRunner()
    result = runner.invoke(bsync, '--version')
    assert result.exit_code == 0
    assert result.stdout_bytes.strip().decode() == f'bsync, version {__version__}'


def test_badargs():
    from bsync.cli import bsync

    runner = CliRunner()
    result = runner.invoke(bsync, '. 123 --settings=does.not.exist.json')
    assert result.exit_code == 2
    assert b'does not exist' in result.stdout_bytes
