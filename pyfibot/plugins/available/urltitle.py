import re
import os
import traceback
from fnmatch import fnmatch
from inspect import getmembers, isfunction
from urllib.parse import urlsplit, parse_qs
from pluginbase import PluginBase
from pyfibot.decorators import init, listener

# http://stackoverflow.com/a/30408189
url_regex = re.compile(
    r'(?:(?:https?|ftp)://)(?:\S+(?::\S*)?@)?(?:(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])' +
    r'(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|' +
    r'(?:(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]+-?)' +
    r'*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:/[^\s]*)?'
)

here = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
plugin_base = PluginBase(package='pyfibot.plugins.urltitle.urltitle_handlers')
plugin_source = plugin_base.make_plugin_source(searchpath=[os.path.join(here, 'urltitle_handlers')])


class URL(object):
    def __init__(self, bot, url):
        self.bot = bot
        self.url = url
        self.components = urlsplit(url)
        self.domain = self.components.netloc
        self.path = self.components.path
        self.query_parameters = parse_qs(self.components.query)
        self.clean_url = url.replace('%s://' % self.components.scheme, '').replace('www.', '')

    def __repr__(self):
        return '<URL "%s">' % self.url

    def get_title(self):
        title = None

        for matcher, handler in handlers.items():
            if handler._is_regex:
                match = matcher.match(self.clean_url)
                if not match:
                    continue
                title = handler(self.bot, self, match)
                break

            if fnmatch(self.clean_url, matcher):
                title = handler(self.bot, self)
                break

        if title is None:
            # Implement get_video_info, get_fragment and get_opengraph_title here.
            pass

        if check_reduntant:
            # Redundancy -check here.
            pass

        return title

    def get_video_info(self):
        # Get (possible) video information using Youtube-DL.
        return

    def get_fragment(self):
        # According to Google's Making AJAX Applications Crawlable specification
        return

    def get_open_graph_title(self):
        # Try and get title meant for social media first, it's usually fairly accurate
        return

    def is_redundant(self, title):
        ''' Returns True if the url and title are similar enough. '''
        return


@init
def init_urltitle(bot):
    global handlers
    global check_reduntant
    handlers = discover_handlers()
    check_reduntant = bot.core_configuration.get('urltitle', {}).get('check_reduntant', False)


@listener
def get_urls(bot, sender, message, raw_message):
    urls = set(re.findall(url_regex, message))
    if not urls:
        return

    for url in urls:
        title = URL(bot, url).get_title()

        if title is False:
            print('Title returned as False -> not printing.')
            return

        if isinstance(title, str):
            return bot.respond(title, raw_message)

    return bot.respond('Detected %i urls.' % len(urls), raw_message)


def discover_handlers():
    url_handlers = {}
    for plugin_name in plugin_source.list_plugins():
        try:
            plugin = plugin_source.load_plugin(plugin_name)
        except:
            print('Failed to load plugin "%s".' % plugin_name)
            traceback.print_exc()
            continue

        for member in getmembers(plugin):
            func = member[1]
            if not isfunction(func):
                continue

            if getattr(func, '_is_urlhandler', False) is True:
                url_handlers[func._url_matcher] = func

    return url_handlers
