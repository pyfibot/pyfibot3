import os
import click
from pyfibot.core import Core


@click.command()
@click.option(
    '-f',
    '--configuration-file',
    type=click.Path(
        exists=False,
        file_okay=True,
        dir_okay=False,
        resolve_path=True
    ),
    default=os.path.expanduser('~/.config/pyfibot/pyfibot.yml')
)
@click.option('-l', '--log-level', type=click.Choice(['debug', 'info', 'warning', 'error']), default='info')
def main(configuration_file, log_level):
    try:
        core = Core(configuration_file=configuration_file, log_level=log_level)
    except IOError:
        return
    core.run()


if __name__ == '__main__':
    main()
