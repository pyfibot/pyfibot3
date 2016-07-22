from pyfibot.decorators import admin_command


@admin_command('reload_modules')
def reload_modules(bot, sender, message, message_arguments):
    ''' Reload bot modules. Only for admins. '''
    bot.load_plugins()
    bot.respond('Modules reloaded.', message_arguments)
