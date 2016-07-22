from pyfibot.decorators import command


@command(['echo', 'toista'])
def echo(bot, sender, message, message_arguments):
    bot.respond(message, message_arguments)
