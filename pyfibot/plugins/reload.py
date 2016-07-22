from pyfibot.decorators import admin_command


@admin_command('reload_plugins')
def reload_plugins(bot, sender, message, raw_message):
    ''' Reload bot plugins. Only for admins. '''
    bot.load_plugins()
    bot.respond('Plugins reloaded.', raw_message)


@admin_command('reload_configuration')
def reload_configuration(bot, sender, message, raw_message):
    ''' Reload bot configuration. Only for admins. '''
    bot.core.load_configuration()
    bot.respond('Configuration reloaded.', raw_message)
