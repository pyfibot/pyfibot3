from pyfibot.decorators import command


@command(['echo', 'toista'])
def echo(bot, sender, message, message_arguments):
    ''' Echoes back the user message. '''
    bot.respond(message, message_arguments)
