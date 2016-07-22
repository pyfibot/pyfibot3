def initialize(func):
    func._is_init = True
    return func


def teardown(func):
    func._is_teardown = True
    return func


def listener(func):
    func._is_listener = True
    return func


class command(object):
    def __init__(self, command_name):
        self.command_name = command_name

    def __call__(self, func):
        def command_wrapper(bot, sender, message, message_arguments):
            return func(bot, sender, message, message_arguments)

        command_wrapper._command = self.command_name
        command_wrapper._is_command = True
        return command_wrapper


class admin_command(object):
    def __init__(self, command_name):
        self.command_name = command_name

    def __call__(self, func):
        def command_wrapper(bot, sender, message, message_arguments):
            return func(bot, sender, message, message_arguments)

        command_wrapper._command = self.command_name
        command_wrapper._is_command = True
        command_wrapper._is_admin_command = True
        return command_wrapper
