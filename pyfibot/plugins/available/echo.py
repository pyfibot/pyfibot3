from pyfibot.decorators import command


@command(['echo', 'toista'])
def echo(bot, sender, message, raw_message):
    ''' Echoes back the user message. '''
    bot.respond(message, raw_message)
