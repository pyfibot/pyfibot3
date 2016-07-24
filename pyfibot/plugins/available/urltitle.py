import re
import os
import traceback
from fnmatch import fnmatch
from inspect import getmembers, isfunction
from urllib.parse import urlsplit, parse_qs
from pluginbase import PluginBase
from datetime import datetime
from dateutil.tz import tzutc
import youtube_dl
from pyfibot.decorators import init, listener
from pyfibot.utils import get_duration_string, get_views_string, get_relative_time_string, parse_datetime


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

        for fetcher in [self.get_video_info]:
            title = fetcher()
            if title is not None:
                break

        if check_reduntant:
            # Redundancy -check here.
            pass

        return title

    def get_video_info(self):
        ''' Gets (possible) video information using YoutubeDL. '''
        with youtube_dl.YoutubeDL(params={'extract_flat': True}) as ydl:
            try:
                info = ydl.extract_info(self.url, download=False)
            except youtube_dl.utils.DownloadError:
                return None

        title = [
            '"%s"' % info.get('title', '')
        ]
        additional_info = []

        uploader = info.get('uploader')
        if uploader:
            title.append('by %s' % uploader)

        duration = info.get('duration')
        if duration:
            additional_info.append(get_duration_string(duration))

        view_count = info.get('view_count')
        if view_count:
            additional_info.append('%s views' % get_views_string(view_count))

        timestamp = info.get('timestamp')
        if timestamp:
            additional_info.append(
                'uploaded %s' % get_relative_time_string(
                    datetime.fromtimestamp(timestamp, tzutc())
                )
            )
        else:
            date = info.get('upload_date') or info.get('release_date')
            if date:
                additional_info.append('uploaded %s' % get_relative_time_string(parse_datetime(date)))

        age_limit = info.get('age_limit')
        if age_limit:
            additional_info.append('%i+' % age_limit)

        title = ' '.join(filter(None, title))
        additional_info = ' - '.join(filter(None, additional_info))

        if not title:
            return None

        if additional_info:
            return '%s [%s]' % (title, additional_info)
        return title

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
