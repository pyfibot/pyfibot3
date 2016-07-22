from slugify import slugify
from pyfibot.decorators import listener
from pyfibot.utils import get_utc_datetime
from pyfibot.database import Database


@listener
def save_message(bot, sender, message, message_arguments):
    target = message_arguments.get('target')
    # Don't save, if target is not defined or this is a private message.
    if not target or target == bot.nickname:
        return

    with Database(bot) as db:
        table = db[slugify('log-%s-%s' % (bot.name, target))]
        table.insert({
            'time': get_utc_datetime(),
            'sender': sender,
            'target': message_arguments.get('target', 'unknown'),
            'message': message,
        })
