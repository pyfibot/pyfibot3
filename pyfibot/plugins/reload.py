from pyfibot.plugin import Plugin


class Reload(Plugin):
    @Plugin.admin_command('reload_plugins')
    def reload_plugins(self, sender, message, raw_message):
        ''' Reload bot plugins. Only for admins. '''
        self.bot.load_plugins()
        self.bot.respond('Plugins reloaded.', raw_message)

    @Plugin.admin_command('reload_configuration')
    def reload_configuration(self, sender, message, raw_message):
        ''' Reload bot configuration. Only for admins. '''
        self.bot.core.load_configuration()
        self.bot.respond('Configuration reloaded.', raw_message)
