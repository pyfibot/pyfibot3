from inspect import getmembers, isfunction


class Plugin(object):
    def __init__(self, bot, plugin_name, plugin):
        self.bot = bot
        self.name = plugin_name
        self._plugin = plugin

        self.init = None
        self.commands = {}
        self.listeners = []
        self.teardown = None
        self.discover_methods()

    def discover_methods(self):
        for member in getmembers(self._plugin):
            func = member[1]
            if not isfunction(func):
                continue

            if getattr(func, '_is_init', False) is True:
                self.init = func
                continue

            if getattr(func, '_is_teardown', False) is True:
                self.teardown = func
                continue

            if getattr(func, '_is_command', False) is True:
                command = getattr(func, '_command', None)

                # TODO: possibly remove the possibility for a list?
                #       additional commands can be registered in init-function if necessary
                #       would make the API more consistent
                if isinstance(command, list):
                    for c in command:
                        self.commands[c] = func

                if isinstance(command, str):
                    self.commands[command] = func

                continue

            if getattr(func, '_is_listener', False) is True:
                self.listeners.append(func)
