from pyfibot.decorators import admin_command


@admin_command('reload_plugins')
def reload_plugins(bot, sender, message, message_arguments):
    ''' Reload bot plugins. Only for admins. '''
    bot.load_plugins()
    bot.respond('Plugins reloaded.', message_arguments)


@admin_command('reload_configuration')
def reload_configuration(bot, sender, message, message_arguments):
    ''' Reload bot configuration. Only for admins. '''
    bot.core.load_configuration()
    bot.respond('Configuration reloaded.', message_arguments)
