import os
import yaml
import asyncio
import requests
from pyfibot.protocol.irc import IRC


class Core(object):
    def __init__(self, configuration_file='~/.config/pyfibot/pyfibot.yml', log_level='info'):
        self.networks = {}
        self.configuration = {}
        self.admins = []

        self.load_configuration(configuration_file)
        self.nickname = self.configuration.get('nick', 'pyfibot')
        self.realname = self.configuration.get('realname', 'https://github.com/lepinkainen/pyfibot')
        self.command_char = self.configuration.get('command_char', '.')
        self.load_networks()

    def run(self):
        loop = self.connect_networks()
        loop.run_forever()

    def load_configuration(self, configuration_file):
        self.configuration_file = os.path.abspath(os.path.expanduser(configuration_file))
        self.configuration_path = os.path.dirname(self.configuration_file)

        if not os.path.exists(self.configuration_file):
            print('Configuration file does not exist in "%s". Creating an example configuration for editing.' % (self.configuration_file))
            raise IOError

        with open(self.configuration_file, 'r') as f:
            self.configuration = yaml.load(f)

        self.admins = self.configuration.get('admins', [])

    def load_networks(self):
        for name, network_configuration in self.configuration.get('networks', {}).items():
            protocol = network_configuration.get('protocol', 'irc')
            if protocol == 'irc':
                self.networks[name] = IRC(core=self, name=name, network_configuration=network_configuration)

    def connect_networks(self):
        loop = asyncio.get_event_loop()
        for network in self.networks.values():
            network.connect(loop)
        return loop

    def get_url(self, url, nocache=False, params=None, headers=None, cookies=None):
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
