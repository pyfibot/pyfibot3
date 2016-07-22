import os
from inspect import getmembers, isfunction
from pluginbase import PluginBase


class Bot(object):
    ''' Base bot object to define common functionalities for all bots. NOT TO BE USED DIRECTLY! '''
    def __init__(self, core, name):
        self._bot = None

        self.core = core
        self.name = name
        self.callbacks = {}

        self.load_configuration()

    @property
    def core_configuration(self):
        ''' Get core configuration. '''
        return self.core.configuration

    @property
    def network_configuration(self):
        ''' Get network configuration. '''
        return self.core_configuration.get('networks', {}).get(self.name, {})

    def load_configuration(self):
        network_configuration = self.network_configuration

        print('Reloading network configuration for "%s".' % (self.name))
        self.nickname = network_configuration.get('nick') or self.core.nickname
        self.command_char = network_configuration.get('command_char') or self.core.command_char

        self.admins = self.core.admins + network_configuration.get('admins', [])
        self.load_plugins()

    def init_callbacks(self):
        for teardown in self.teardowns:
            teardown(self._bot)

        self.callbacks = {
            'commands': self._get_builtin_commands(),
            'listeners': [],
            'teardowns': [],
        }

    @property
    def commands(self):
        return self.callbacks.get('commands', {})

    @property
    def listeners(self):
        return self.callbacks.get('listeners', [])

    @property
    def teardowns(self):
        return self.callbacks.get('teardowns', [])

    def is_admin(self, raw_message):
        ''' Get users admin status. '''
        return False

    def connect(self):
        ''' Connect to server. '''
        raise NotImplementedError

    def cleanup_response(self, response):
        return response.strip()

    def respond(self, message, raw_message):
        ''' Respond to message sent to the bot. '''
        raise NotImplementedError

    def get_command(self, message):
        '''
        Gets command from message.
        @return command, message_without_command
        '''
        command = message.split(' ')[0].replace(self.command_char, '').strip()
        message_without_command = message.replace('%s%s' % (self.command_char, command), '').strip()
        return command, message_without_command

    def handle_message(self, sender, message, raw_message={}):
        ''' Message handler, calling all listeners, parsing and running commands if found. '''
        # Don't react to own messages.
        if sender == self.nickname:
            return

        for listener in self.listeners:
            self.core.loop.run_in_executor(None, listener, self, sender, message, raw_message)

        if message.startswith(self.command_char):
            command, message_without_command = self.get_command(message)

            if not command:
                return

            if command in self.commands.keys():
                if getattr(self.commands[command], '_is_admin_command', False) is True and not self.is_admin(raw_message):
                    return self.respond('This command is only for admins.', raw_message)
                self.core.loop.run_in_executor(None, self.commands[command], self, sender, message_without_command, raw_message)

    def _get_builtin_commands(self):
        ''' Gets commands built in to the bot. '''
        return {
            'help': self.command_help,
        }

    def load_plugins(self):
        ''' (Re)loads all plugins, calling teardowns before unloading them. '''
        here = os.path.abspath(os.path.dirname(__file__))
        self.plugin_base = PluginBase(package='pyfibot.plugins')
        self.plugin_source = self.plugin_base.make_plugin_source(searchpath=[os.path.abspath(os.path.join(here, '../plugins'))])

        # Re-initialize all callback functions.
        self.init_callbacks()

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

                    # TODO: possibly remove the possibility for a list?
                    #       additional commands can be registered in init-function if necessary
                    #       would make the API more consistent
                    if isinstance(command, list):
                        for c in command:
                            self.register_command(c, func)

                    if isinstance(command, str):
                        self.register_command(command, func)

                    continue

                if getattr(func, '_is_listener', False) is True:
                    self.register_listener(func)

            print('Loaded plugin "%s".' % plugin_name)

    def command_help(self, bot, sender, message, raw_message):
        ''' Get help for bot plugins '''
        if not message:
            self.respond(
                'Available commands for users are: %s' % (
                    ', '.join(sorted([
                        command
                        for command, function in self.commands.items() if getattr(function, '_is_admin_command', False) is False
                    ]))
                ),
                raw_message=raw_message
            )
            # In addition to the normal commands, give admin commands to admins.
            if self.is_admin(raw_message):
                self.respond(
                    'Available commands for admins are: %s' % (
                        ', '.join(sorted([
                            command
                            for command, function in self.commands.items() if getattr(function, '_is_admin_command', False) is True
                        ]))
                    ),
                    raw_message=raw_message
                )
            return

        if message not in self.commands.keys():
            return self.respond(
                'Command "%s" unknown. Available commands are: %s' % (
                    message,
                    ', '.join(sorted(self.commands.keys()))
                ),
                raw_message=raw_message
            )

        docstring = self.commands[message].__doc__
        if not docstring:
            return self.respond('Command "%s" has no help.' % message, raw_message=raw_message)
        self.respond(docstring.split('\n')[0], raw_message=raw_message)

    def register_command(self, command, function_handle):
        ''' Registers command to the bot. '''
        if command in self.commands.keys():
            print('Command "%s" from "%s" would override existing command -> ignoring.' % (command, function_handle.__name__))
            return
        self.callbacks['commands'][command] = function_handle

    def register_listener(self, function_handle):
        ''' Registers listener to the bot. '''
        self.callbacks['listeners'].append(function_handle)

    def register_teardown(self, function_handle):
        ''' Registers plugin teardown function to the bot. '''
        self.callbacks['teardowns'].append(function_handle)

    def get_url(self, url, nocache=False, params=None, headers=None, cookies=None):
        return self.core.get_url(url, nocache=nocache, params=params, headers=headers, cookies=cookies)

    def get_bs(self, url, nocache=False, params=None, headers=None, cookies=None):
        return self.core.get_bs(url, nocache=nocache, params=params, headers=headers, cookies=cookies)
