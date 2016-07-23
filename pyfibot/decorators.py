import re


def init(func):
    '''
    Decorator for plugin initialization. Runs when plugin is (re)loaded.

        @init
        def init_plugin(bot):
            pass
    '''
    func._is_init = True
    return func


def teardown(func):
    '''
    Decorator for plugin teardown. Runs before plugin is unloaded.

        @teardown
        def teardown_plugin(bot):
            pass
    '''
    func._is_teardown = True
    return func


def listener(func):
    '''
    Decorator to build listener listening all messages sent to the bot.

        @listener
        def print_all(bot, sender, message, raw_message):
            print(sender, message)
    '''
    func._is_listener = True
    return func


class command(object):
    '''
    Decorator to build commands to the bot.

        @command('echo')
        def echo(bot, sender, message, raw_message):
            bot.respond(message, raw_message)
    '''
    def __init__(self, command_name):
        self.command_name = command_name

    def __call__(self, func):
        def command_wrapper(bot, sender, message, raw_message):
            return func(bot, sender, message, raw_message)

        command_wrapper._command = self.command_name
        command_wrapper._is_command = True
        return command_wrapper


class admin_command(object):
    '''
    Decorator to build administrator commands to the bot.

        @admin_command('admin_echo')
        def admin_echo(bot, sender, message, raw_message):
            bot.respond(message, raw_message)
    '''
    def __init__(self, command_name):
        self.command_name = command_name

    def __call__(self, func):
        def command_wrapper(bot, sender, message, raw_message):
            return func(bot, sender, message, raw_message)

        command_wrapper._command = self.command_name
        command_wrapper._is_command = True
        command_wrapper._is_admin_command = True
        return command_wrapper


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
