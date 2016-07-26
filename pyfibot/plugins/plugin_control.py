import os
from fnmatch import fnmatch
from pyfibot.plugin import Plugin


class PluginControl(Plugin):
    ENABLED_PLUGINS_DIR = os.path.abspath(os.path.dirname(__file__))

    def get_python_scripts(self, directory):
        return {
            filename.replace('.py', ''): os.path.join(directory, filename)
            for filename in os.listdir(directory) if fnmatch(filename, '*.py') and filename != '__init__.py'
        }

    def get_enabled_plugins(self):
        return self.get_python_scripts(self.ENABLED_PLUGINS_DIR)

    def get_available_plugins(self):
        return self.get_python_scripts(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'available'))

    @Plugin.admin_command('available_plugins')
    def list_available_plugins(self, sender, message, raw_message):
        ''' List all available bot plugins. Only for admins. '''

        enabled_plugins = self.get_enabled_plugins().keys()
        available_plugins = [
            plugin
            for plugin in self.get_available_plugins().keys() if plugin not in enabled_plugins
        ]
        self.bot.respond('Available plugins: %s' % (', '.join(sorted(available_plugins))), raw_message)

    @Plugin.admin_command('enabled_plugins')
    def list_enabled_plugins(self, sender, message, raw_message):
        ''' List all enabled bot plugins. Only for admins. '''
        enabled_plugins = self.get_enabled_plugins().keys()
        self.bot.respond('Enabled plugins: %s' % (', '.join(sorted(enabled_plugins))), raw_message)

    @Plugin.admin_command('enable_plugin')
    def enable_plugin(self, sender, message, raw_message):
        ''' Enable an available bot plugin. Only for admins. '''
        available_plugins = self.get_available_plugins()
        if message not in available_plugins.keys():
            return self.bot.respond('Plugin "%s" does not exist.' % message, raw_message)

        if message in self.get_enabled_plugins().keys():
            return self.bot.respond('Plugin "%s" is already enabled.' % message, raw_message)

        os.symlink(available_plugins[message], os.path.join(self.ENABLED_PLUGINS_DIR, '%s.py' % message))

        self.bot.load_plugins()
        self.bot.respond('Plugin "%s" enabled.' % message, raw_message)

    @Plugin.admin_command('disable_plugin')
    def disable_plugin(self, sender, message, raw_message):
        ''' Disable a bot plugin. Only for admins. '''
        enabled_plugins = self.get_enabled_plugins()
        if message not in enabled_plugins.keys():
            return self.bot.respond('Plugin "%s" isn\'t enabled.' % message, raw_message)

        if not os.path.islink(enabled_plugins[message]):
            return self.bot.respond('Plugin "%s" is a core plugin and cannot be disabled.' % message, raw_message)

        os.unlink(enabled_plugins[message])

        self.bot.load_plugins()
        self.bot.respond('Plugin "%s" disabled.' % message, raw_message)
