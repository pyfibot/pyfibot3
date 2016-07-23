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
    Decorator to build commands to the bot.

        @command('echo')
        def echo(bot, sender, message, raw_message):
            bot.respond(message, raw_message)
    '''
    def __init__(self, url_matcher):
        self.url_matcher = url_matcher

    def __call__(self, func):
        def handler_wrapper(bot, url):
            return func(bot, url)

        handler_wrapper._is_urlhandler = True
        handler_wrapper._url_matcher = self.url_matcher
        return handler_wrapper
