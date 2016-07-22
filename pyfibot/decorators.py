def init(func):
    '''
    Decorator for module initialization. Runs when module is (re)loaded.

        @init
        def init_module(bot):
            pass
    '''
    func._is_init = True
    return func


def teardown(func):
    '''
    Decorator for module teardown. Runs before module is unloaded.

        @teardown
        def teardown_module(bot):
            pass
    '''
    func._is_teardown = True
    return func


def listener(func):
    '''
    Decorator to build listener listening all messages sent to the bot.

        @listener
        def print_all(bot, sender, message, message_arguments):
            print(sender, message)
    '''
    func._is_listener = True
    return func


class command(object):
    '''
    Decorator to build commands to the bot.

        @command('echo')
        def echo(bot, sender, message, message_arguments):
            bot.respond(message, message_arguments)
    '''
    def __init__(self, command_name):
        self.command_name = command_name

    def __call__(self, func):
        def command_wrapper(bot, sender, message, message_arguments):
            return func(bot, sender, message, message_arguments)

        command_wrapper._command = self.command_name
        command_wrapper._is_command = True
        return command_wrapper


class admin_command(object):
    '''
    Decorator to build administrator commands to the bot.

        @admin_command('admin_echo')
        def admin_echo(bot, sender, message, message_arguments):
            bot.respond(message, message_arguments)
    '''
    def __init__(self, command_name):
        self.command_name = command_name

    def __call__(self, func):
        def command_wrapper(bot, sender, message, message_arguments):
            return func(bot, sender, message, message_arguments)

        command_wrapper._command = self.command_name
        command_wrapper._is_command = True
        command_wrapper._is_admin_command = True
        return command_wrapper
