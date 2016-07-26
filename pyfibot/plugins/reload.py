from pyfibot.plugin import Plugin


class Reload(Plugin):
    @Plugin.admin_command('reload')
    def reload(self, sender, message, raw_message):
        if message == 'plugins':
            return self.reload_plugins(sender, message, raw_message=raw_message)
        if message == 'configuration':
            return self.reload_configuration(sender, message, raw_message=raw_message)
        return self.bot.respond('Usage: %sreload <plugins|configuration>' % self.bot.command_char, raw_message)

    def reload_plugins(self, sender, message, raw_message):
        ''' Reload bot plugins. Only for admins. '''
        self.bot.load_plugins()
        self.bot.respond('Plugins reloaded.', raw_message)

    def reload_configuration(self, sender, message, raw_message):
        ''' Reload bot configuration. Only for admins. '''
        self.bot.core.load_configuration()
        self.bot.respond('Configuration reloaded.', raw_message)
