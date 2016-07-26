from slugify import slugify
from pyfibot.plugin import Plugin
from pyfibot.utils import get_utc_datetime
from pyfibot.database import Database


class Logger(Plugin):
    @Plugin.listener()
    def save_message(self, sender, message, raw_message):
        ''' Log all messages to database. '''
        target = raw_message.get('target')
        # Don't save, if target is not defined or this is a private message.
        if not target or target == self.bot.nickname:
            return

        with Database(self.bot) as db:
            table = db[slugify('log-%s-%s' % (self.bot.name, target))]
            table.insert({
                'time': get_utc_datetime(),
                'sender': sender,
                'target': raw_message.get('target', 'unknown'),
                'message': message,
            })
