import os
from inspect import getmembers, isfunction
from pluginbase import PluginBase


class Protocol(object):
    def __init__(self, core, name, network_configuration):
        self._bot = None

        self.core = core
        self.name = name

        self.nickname = network_configuration.get('nick') or self.core.nickname
        self.command_char = network_configuration.get('command_char') or self.core.command_char

        self.admins = self.core.admins + network_configuration.get('admins', [])

        self.commands = {}
        self.listeners = []
        self.teardowns = []

        self.load_plugins()

    @property
    def core_configuration(self):
        return self.core.configuration

    def is_admin(self, message_arguments):
        return False

    def connect(self, loop):
        raise NotImplementedError

    def respond(self, message, message_arguments):
        raise NotImplementedError

    def get_command(self, message):
        command = message.split(' ')[0].replace('.', '').strip()
        message_without_command = message.replace('.%s' % command, '').strip()
        return command, message_without_command

    def handle_message(self, sender, message, message_arguments={}):
        # Don't react to own messages.
        if sender == self.nickname:
            return

        for listener in self.listeners:
            listener(self, sender, message, message_arguments=message_arguments)

        if message.startswith(self.command_char):
            command, message_without_command = self.get_command(message)

            if not command:
                return

            if command in self.commands.keys():
                if getattr(self.commands[command], '_is_admin_command', False) is True and not self.is_admin(message_arguments):
                    return self.respond('This command is only for admins.', message_arguments)
                self.commands[command](self, sender, message_without_command, message_arguments=message_arguments)

    def _get_builtin_commands(self):
        return {
            'help': self.command_help,
        }

    def load_plugins(self):
        for teardown in self.teardowns:
            teardown(self._bot)

        here = os.path.abspath(os.path.dirname(__file__))
        self.plugin_base = PluginBase(package='pyfibot.plugins')
        self.plugin_source = self.plugin_base.make_plugin_source(searchpath=[os.path.abspath(os.path.join(here, '../plugins'))])

        self.commands = self._get_builtin_commands()
        self.listeners = []
        self.teardowns = []

        for plugin_name in self.plugin_source.list_plugins():
            try:
                plugin = self.plugin_source.load_plugin(plugin_name)
            except:
                print('Failed to load plugin "%s".' % plugin_name)
                continue

            for member in getmembers(plugin):
                func = member[1]
                if not isfunction(func):
                    continue

                if getattr(func, '_is_init', False) is True:
                    func(self)
                    continue

                if getattr(func, '_is_teardown', False) is True:
                    self.register_teardown(func)
                    continue

                if getattr(func, '_is_command', False) is True:
                    command = getattr(func, '_command', None)

                    if isinstance(command, list):
                        for c in command:
                            self.register_command(c, func)

                    if isinstance(command, str):
                        self.register_command(command, func)

                    continue

                if getattr(func, '_is_listener', False) is True:
                    self.register_listener(func)

    def command_help(self, bot, sender, message, message_arguments):
        ''' Get help for bot modules '''
        if not message:
            return self.respond(
                'Available commands are: %s' % (
                    ', '.join(self.commands.keys())
                ),
                message_arguments=message_arguments
            )
        if message not in self.commands.keys():
            return self.respond(
                'Command "%s" unknown. Available commands are: %s' % (
                    message,
                    ', '.join(self.commands.keys())
                ),
                message_arguments=message_arguments
            )

        docstring = self.commands[message].__doc__
        if not docstring:
            return self.respond('Command "%s" has no help.' % message, message_arguments=message_arguments)
        self.respond(docstring.split('\n')[0], message_arguments=message_arguments)

    def register_command(self, command, function_handle):
        if command in self._get_builtin_commands().keys():
            print('Command "%s" would override built-in command -> ignoring.' % command)
            return
        if command in self.commands.keys():
            print('Command "%s" overrides existing command.' % command)
        self.commands[command] = function_handle

    def register_listener(self, function_handle):
        self.listeners.append(function_handle)

    def register_teardown(self, function_handle):
        self.teardowns.append(function_handle)

    def get_url(self, url, nocache=False, params=None, headers=None, cookies=None):
        return self.core.get_url(url, nocache=nocache, params=params, headers=headers, cookies=cookies)
