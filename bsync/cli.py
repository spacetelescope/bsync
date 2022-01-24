from pathlib import Path
from getpass import getuser
from contextlib import nullcontext

import click

from bsync.api import BoxAPI
from bsync.sync import BoxSync


USER = getuser()


@click.command()
@click.argument('source_folder', envvar='SOURCE_FOLDER',
                type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.argument('box_folder_id', envvar='BOX_FOLDER_ID', type=int)
@click.option('-u', '--box-user', default=USER, envvar='BOX_USER',
              help=f'User account name on Box.com. Defaults to {USER}')
@click.option('-s', '--settings', envvar='BOX_SETTINGS_FILE',
              type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option('-i', '--ipdb', is_flag=True, help='Drop into ipdb shell on error')
@click.option('-o', '--output', help='File to write created items as CSV report')
def bsync(**options):
    """
    Syncs the contents of local folder to your Box account

    SOURCE_FOLDER is the path of an existing folder

    BOX_FOLDER_ID is the ID for the folder in Box where you want the files sent
    """
    click.echo(options)
    ctx = nullcontext
    if options['ipdb']:
        from ipdb import launch_ipdb_on_exception
        ctx = launch_ipdb_on_exception
    with ctx():
        api = BoxAPI(options)
        bsync = BoxSync(options, api)
        bsync()
        if options['output']:
            bsync.output(options['output'])


if __name__ == '__main__':
    import ipdb
    with ipdb.launch_ipdb_on_exception():
        bsync()