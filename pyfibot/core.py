import os
import sys
import click
import yaml
import asyncio
import logging
from pyfibot import coloredlogger


class Core(object):
    ''' Bot core, holding the configuration and connecting to bots. '''

    def __init__(self, configuration_file='~/.config/pyfibot/pyfibot.yml', log_level='info', daemonize=False):
        self.loop = asyncio.get_event_loop()
        self.bots = {}
        self.configuration = {}
        self.admins = []
        self.command_char = '.'
        self.configuration_file = os.path.abspath(os.path.expanduser(configuration_file))

        self.logger = self.init_logging(log_level, daemonize)

        self.load_configuration()
        self.nickname = self.configuration.get('nick', 'pyfibot')
        self.realname = self.configuration.get('realname', 'https://github.com/lepinkainen/pyfibot')
        self.load_bots()

    def run(self):
        ''' Run bot. '''
        self.connect_bots()
        self.loop.run_forever()
        self.loop.close()

    @property
    def log(self):
        return logging.getLogger(self.__class__.__name__)

    @property
    def configuration_path(self):
        return os.path.dirname(self.configuration_file)

    @property
    def plugin_path(self):
        return os.path.join(self.configuration_path, 'plugins')

    def init_logging(self, log_level, daemonize=False):
        handlers = []
        if not daemonize:
            message_format = "[%(asctime)-15s][$BOLD%(name)-45s$RESET][%(levelname)-18s] %(message)s ($BOLD%(filename)s$RESET:%(lineno)d)"
            formatter = coloredlogger.ColoredFormatter(coloredlogger.formatter_message(message_format, True))
            console = logging.StreamHandler()
            console.setFormatter(formatter)
            handlers.append(console)
        else:
            message_format = "[%(asctime)-15s][%(name)-45s][%(levelname)-18s] %(message)s (%(filename)s:%(lineno)d)"
            formatter = logging.Formatter(message_format)
            filehandler = logging.FileHandler(filename=os.path.join(self.configuration_path, 'pyfibot.log'), delay=True)
            filehandler.setFormatter(formatter)
            handlers.append(filehandler)

        logging.basicConfig(level=log_level.upper(), handlers=handlers)

    def load_configuration(self):
        ''' (Re)loads configuration from file. '''
        if not os.path.exists(self.plugin_path):
            os.makedirs(self.plugin_path)

        if not os.path.exists(self.configuration_file):
            # TODO: Maybe actually create the example conf?
            print('Configuration file does not exist in "%s". Creating an example configuration for editing.' % self.configuration_file)
            raise IOError

        with open(self.configuration_file, 'r') as f:
            self.configuration = yaml.load(f)

        self.log.info('Reloading core configuration.')

        self.admins = self.configuration.get('admins', [])
        self.command_char = self.configuration.get('command_char', '.')
        for name, bot in self.bots.items():
            bot.load_configuration()

    def load_bots(self):
        ''' Loads bots from configuration and initializes them. '''
        for name, bot_configuration in self.configuration.get('bots', {}).items():
            protocol = bot_configuration.get('protocol', 'irc')
            if protocol == 'irc':
                from pyfibot.bot.ircbot import IRCbot
                self.bots[name] = IRCbot(core=self, name=name)
            if protocol == 'telegram':
                from pyfibot.bot.telegrambot import TelegramBot
                self.bots[name] = TelegramBot(core=self, name=name)

    def connect_bots(self):
        ''' Creates main event loop and connects to bots. '''
        for bot in self.bots.values():
            bot.connect()


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
@click.option('-l', '--log-level', type=click.Choice(['debug', 'info', 'warning', 'error', 'critical']), default='info')
@click.option('-d', '--daemonize', is_flag=True)
def main(configuration_file, log_level, daemonize):
    try:
        core = Core(configuration_file=configuration_file, log_level=log_level, daemonize=daemonize)
    except IOError:
        return sys.exit(1)

    if daemonize:
        # https://sigterm.sh/2012/08/22/forking-background-processes-in-python/
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(1)
        except OSError as e:
            sys.stderr.write('Fork failed: %d (%s)' % (e.errno, e.strerror))
            sys.exit(1)

    core.run()
