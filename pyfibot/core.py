import os
import click
import yaml
import asyncio
import requests
from bs4 import BeautifulSoup


class Core(object):
    ''' Bot core, holding the configuration and connecting to networks. '''

    def __init__(self, configuration_file='~/.config/pyfibot/pyfibot.yml', log_level='info'):
        self.networks = {}
        self.configuration = {}
        self.admins = []
        self.command_char = '.'
        self.configuration_file = os.path.abspath(os.path.expanduser(configuration_file))

        self.load_configuration()
        self.nickname = self.configuration.get('nick', 'pyfibot')
        self.realname = self.configuration.get('realname', 'https://github.com/lepinkainen/pyfibot')
        self.load_networks()

    def run(self):
        ''' Run bot. '''
        loop = self.connect_networks()
        loop.run_forever()

    def load_configuration(self):
        ''' (Re)loads configuration from file. '''
        self.configuration_path = os.path.dirname(self.configuration_file)

        if not os.path.exists(self.configuration_file):
            # TODO: Maybe actually create the example conf?
            print('Configuration file does not exist in "%s". Creating an example configuration for editing.' % (self.configuration_file))
            raise IOError

        with open(self.configuration_file, 'r') as f:
            self.configuration = yaml.load(f)

        print('Reloading core configuration.')

        self.admins = self.configuration.get('admins', [])
        self.command_char = self.configuration.get('command_char', '.')
        for name, network in self.networks.items():
            network.load_configuration()

    def load_networks(self):
        ''' Loads networks from configuration and initializes them. '''
        for name, network_configuration in self.configuration.get('networks', {}).items():
            protocol = network_configuration.get('protocol', 'irc')
            if protocol == 'irc':
                from pyfibot.bot.ircbot import IRCbot
                self.networks[name] = IRCbot(core=self, name=name)

    def connect_networks(self):
        ''' Creates main event loop and connects to networks. '''
        self.loop = asyncio.get_event_loop()
        for network in self.networks.values():
            network.connect()
        return self.loop

    def get_url(self, url, nocache=False, params=None, headers=None, cookies=None):
        ''' Fetch url. '''
        # TODO: clean-up, straight copy from original pyfibot
        #       possibly add raise_for_status?
        s = requests.session()
        s.stream = True  # Don't fetch content unless asked
        s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0'})
        # Custom headers from requester
        if headers:
            s.headers.update(headers)
        # Custom cookies from requester
        if cookies:
            s.cookies.update(cookies)

        try:
            r = s.get(url, params=params)
        except requests.exceptions.InvalidSchema:
            # log.error("Invalid schema in URI: %s" % url)
            return None
        except requests.exceptions.SSLError:
            # log.error("SSL Error when connecting to %s" % url)
            return None
        except requests.exceptions.ConnectionError:
            # log.error("Connection error when connecting to %s" % url)
            return None

        size = int(r.headers.get('Content-Length', 0)) // 1024
        # log.debug("Content-Length: %dkB" % size)
        if size > 2048:
            # log.warn("Content too large, will not fetch: %skB %s" % (size, url))
            return None

        return r

    def get_bs(self, url, nocache=False, params=None, headers=None, cookies=None):
        ''' Fetch BeautifulSoup from url. '''
        # TODO: clean-up, straight copy from original pyfibot
        r = self.get_url(url, nocache=nocache, params=params, headers=headers, cookies=cookies)
        if not r:
            return None

        content_type = r.headers['content-type'].split(';')[0]
        if content_type not in ['text/html', 'text/xml', 'application/xhtml+xml']:
            # log.debug("Content-type %s not parseable" % content_type)
            return None

        if r.content:
            return BeautifulSoup(r.content, 'html.parser')
        return None


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
