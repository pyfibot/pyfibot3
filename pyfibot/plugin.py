import os
import sys
from inspect import getmembers, isclass, ismethod
from pluginbase import PluginBase
from pyfibot.coloredlogger import ColoredLogger
from pyfibot.periodic_task import PeriodicTask


class Plugin(object):
    def __init__(self, bot):
        self.name = self.__class__.__name__
        self.bot = bot
        self.init()
        self._periodic_tasks = []
        self.__discover_methods()
        self.log.info('Loaded plugin "%s".' % self.name)

    @property
    def log(self):
        return ColoredLogger('plugin.%s' % self.name)

    def __discover_methods(self):
        for member in getmembers(self):
            func = member[1]
            if not ismethod(func):
                continue

            if getattr(func, '_is_command', False) is True:
                command = getattr(func, '_command', None)

                # TODO: possibly remove the possibility for a list?
                #       additional commands can be registered in init-function if necessary
                #       would make the API more consistent
                if isinstance(command, list):
                    for c in command:
                        self.bot.register_command(c, func)

                if isinstance(command, str):
                    self.bot.register_command(command, func)

                continue

            if getattr(func, '_is_listener', False) is True:
                self.bot.register_listener(func)
                continue

            if getattr(func, '_is_interval', False) is True:
                self._periodic_tasks.append(PeriodicTask(func, func._interval, self.bot))

    @classmethod
    def discover_plugins(cls, bot):
        here = os.path.abspath(os.path.dirname(__file__))
        config_dir = os.path.join(bot.core.configuration_path, 'plugins')

        cls.plugin_base = PluginBase(package='pyfibot.plugins')
        cls.plugin_source = cls.plugin_base.make_plugin_source(searchpath=[
            os.path.abspath(os.path.join(here, 'plugins')),
            config_dir,
        ])

        for plugin_name in cls.plugin_source.list_plugins():
            plugin = cls.plugin_source.load_plugin(plugin_name)
            for member in getmembers(plugin):
                # Filter out unwanted objects...
                if not isclass(member[1]) or not issubclass(member[1], Plugin) or member[1] == Plugin:
                    continue

                try:
                    yield member[1](bot)
                except:
                    bot.log.error('Failed to load plugin "%s".' % plugin_name, exc_info=sys.exc_info())

    def init(self):
        pass

    def teardown(self):
        pass

    @property
    def config(self):
        return self.bot.core.configuration.get('plugin', {}).get(self.name.lower(), {})

    # DECORATORS
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
                try:
                    return func(bot, sender, message, raw_message)
                except:
                    bot.log.error('Error running command "%s".' % self.command_name, exc_info=sys.exc_info())

            command_wrapper._command = self.command_name
            command_wrapper._is_command = True
            command_wrapper.__doc__ = func.__doc__
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
                try:
                    return func(bot, sender, message, raw_message)
                except:
                    bot.log.error('Error running command "%s".' % self.command_name, exc_info=sys.exc_info())

            command_wrapper._command = self.command_name
            command_wrapper._is_command = True
            command_wrapper._is_admin_command = True
            command_wrapper.__doc__ = func.__doc__
            return command_wrapper

    class listener(object):
        '''
        Decorator to build listener listening all messages sent to the bot.

        @listener
        def print_all(bot, sender, message, raw_message):
            print(sender, message)
        '''
        def __call__(self, func):
            def listener_wrapper(bot, sender, message, raw_message):
                try:
                    return func(bot, sender, message, raw_message)
                except:
                    bot.log.error('Error running listener.', exc_info=sys.exc_info())

            listener_wrapper._is_listener = True
            return listener_wrapper

    class interval(object):
        def __init__(self, interval, run_on_init=False):
            self.interval = int(interval)
            self.run_on_init = run_on_init

        def __call__(self, func):
            func._is_interval = True
            func._interval = self.interval
            func._run_on_init = self.run_on_init
            return func
