import re
import os
import traceback
from fnmatch import fnmatch
from inspect import getmembers, isfunction
from urllib.parse import urlsplit, urlunsplit, parse_qs
from pluginbase import PluginBase
from datetime import datetime
from dateutil.tz import tzutc
import youtube_dl
from pyfibot.utils import get_duration_string, get_views_string, get_relative_time_string, parse_datetime


class URL(object):
    # http://stackoverflow.com/a/30408189
    url_regex = re.compile(
        r'(?:(?:https?|ftp)://)(?:\S+(?::\S*)?@)?(?:(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])' +
        r'(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|' +
        r'(?:(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]+-?)' +
        r'*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:/[^\s]*)?'
    )

    here = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    plugin_base = PluginBase(package='pyfibot.url.handlers')
    plugin_source = plugin_base.make_plugin_source(searchpath=[os.path.join(here, 'handlers')])

    def __init__(self, url):
        self.url = url
        self.components = urlsplit(url)
        self.domain = self.components.netloc
        self.path = self.components.path
        self.query_parameters = parse_qs(self.components.query)
        self.clean_url = url.replace('%s://' % self.components.scheme, '').replace('www.', '')
        self.handlers = self.discover_handlers()

    def __repr__(self):
        return '<URL "%s">' % self.url

    @classmethod
    def get_urls(cls, string):
        return [URL(url) for url in set(re.findall(cls.url_regex, string))]

    def discover_handlers(self):
        print('Discovering URL handlers')
        self.url_handlers = {}
        for plugin_name in self.plugin_source.list_plugins():
            try:
                plugin = self.plugin_source.load_plugin(plugin_name)
            except:
                print('Failed to load url handler "%s".' % plugin_name)
                traceback.print_exc()
                continue

            for member in getmembers(plugin):
                func = member[1]
                if not isfunction(func):
                    continue

                if getattr(func, '_is_urlhandler', False) is True:
                    self.url_handlers[func._url_matcher] = func

        return self.url_handlers

    def get_title(self, bot, check_reduntant=False):
        title = None

        for matcher, handler in self.handlers.items():
            if handler._is_regex:
                match = matcher.match(self.clean_url)
                if not match:
                    continue
                return handler(bot, self, match)

            if fnmatch(self.clean_url, matcher):
                return handler(bot, self)

        title = self.get_video_info()
        if title:
            return title

        # Fallback to generic handler
        bs = bot.get_bs(self.url)
        if not bs:
            # If fetching BS failed, return False
            # log.debug("No BS available, returning")
            return

        bs = self.get_fragment(bot, bs)
        title = self.get_generic_title(bs)

        if check_reduntant and self.check_reduntant(title):
            return

        return title

    def get_video_info(self):
        ''' Gets (possible) video information using YoutubeDL. '''
        with youtube_dl.YoutubeDL(params={'extract_flat': True}) as ydl:
            try:
                info = ydl.extract_info(self.url, download=False)
            except youtube_dl.utils.DownloadError:
                return None

        video_title = info.get('title')
        if not video_title:
            return

        title = ['"%s"' % video_title]
        additional_info = []

        uploader = info.get('uploader')
        if uploader:
            title.append('by %s' % uploader)

        is_live = info.get('is_live', False)
        if is_live:
            additional_info.append('LIVE')

        if not is_live:
            duration = info.get('duration')
            if duration:
                additional_info.append(get_duration_string(duration))

        average_rating = info.get('average_rating')
        if average_rating:
            additional_info.append('%.0f/5' % average_rating)

        view_count = info.get('view_count')
        if view_count:
            additional_info.append('%s views' % get_views_string(view_count))

        if not is_live:
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

        # If this is a playlist, there's certain number of entries
        entries = info.get('entries')
        if entries:
            additional_info.append('%i entries' % len(entries))

        tags = info.get('tags')
        if tags:
            additional_info.append(', '.join(tags[:4]))

        title = ' '.join(filter(None, [x.strip() for x in title]))
        additional_info = ' - '.join(filter(None, [x.strip() for x in additional_info]))

        if not title:
            return None

        if additional_info:
            return ('%s [%s]' % (title, additional_info)).strip()
        return title.strip()

    # https://developers.google.com/webmasters/ajax-crawling/docs/specification
    def __escaped_fragment(self, url, meta=False):
        url = urlsplit(url)
        if not url.fragment or not url.fragment.startswith('!'):
            if not meta:
                return url.geturl()

        query = url.query
        if query:
            query += '&'
        query += '_escaped_fragment_='
        if url.fragment:
            query += url.fragment[1:]

        return urlunsplit((url.scheme, url.netloc, url.path, query, ''))

    def get_fragment(self, bot, bs):
        # According to Google's Making AJAX Applications Crawlable specification
        fragment = bs.find('meta', {'name': 'fragment'})
        if fragment and fragment.get('content') == '!':
            # log.debug("Fragment meta tag on page, getting non-ajax version")
            url = self.__escaped_fragment(self.url, meta=True)
            bs = bot.get_url(url)
        return bs

    def get_generic_title(self, bs):
        title = bs.find('meta', {'property': 'og:title'})
        if not title:
            title = bs.find('title')
            # no title attribute
            if not title:
                # log.debug("No title found, returning")
                return
            title = title.text
        else:
            title = title['content']
        return title

    def is_redundant(self, title):
        ''' Returns True if the url and title are similar enough. '''
        return


class urlhandler(object):
    '''
    Decorator to build urlhandlers for urltitle -plugin.
    url_matcher can either be a string following fnmatch -spec or a (compiled) regex-object.

    The handler itself receives the bot which found the url, an urltitle.URL -object,
    and optionally, a regex match-object (only if the url_matcher is regex-object of course).

    The urls passed to the matcher are stripped from protocol and 'www.' -prefix to make the
    matchers more simple. So for example 'http://www.example.com' becomes 'example.com',
    when looking for a match.

    The handler can return:
        - None (indicating no title was found and should fallback to default behaviour)
        - False (to indicate that this url doesn't need a title)
        - String (to send Title string to channel)

    Examples:

        @urlhandler('github.com/*')
        def github(bot, url):
            # Don't react to Github -urls, as the url itself is enough.
            return False

        @urlhandler(re.compile(r'imdb\.com/title/(?P<imdb_id>tt[0-9]+)/?'))
        def imdb(bot, url, match):
            imdb_id = match.group('imdb_id')
            return

    '''
    def __init__(self, url_matcher):
        self.url_matcher = url_matcher

    def __call__(self, func):
        def handler_string(bot, url):
            return func(bot, url)

        def handler_regex(bot, url, match):
            return func(bot, url, match)

        if isinstance(self.url_matcher, re._pattern_type):
            handler_wrapper = handler_regex
            handler_wrapper._is_regex = True
        else:
            handler_wrapper = handler_string
            handler_wrapper._is_regex = False

        handler_wrapper._is_urlhandler = True
        handler_wrapper._url_matcher = self.url_matcher
        return handler_wrapper
