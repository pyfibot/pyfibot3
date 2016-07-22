from pyfibot.decorators import admin_command


@admin_command('reload')
def reload(bot, sender, message, message_arguments):
    ''' Reload bot modules. Only for admins. '''
    bot.load_plugins()
    bot.respond('Modules reloaded.', message_arguments)
