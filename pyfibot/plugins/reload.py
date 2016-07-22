from pyfibot.decorators import admin_command


@admin_command('reload_modules')
def reload_modules(bot, sender, message, message_arguments):
    ''' Reload bot modules. Only for admins. '''
    bot.load_plugins()
    bot.respond('Modules reloaded.', message_arguments)


@admin_command('reload_configuration')
def reload_configuration(bot, sender, message, message_arguments):
    ''' Reload bot configuration. Only for admins. '''
    bot.core.load_configuration()
    bot.respond('Configuration reloaded.', message_arguments)
