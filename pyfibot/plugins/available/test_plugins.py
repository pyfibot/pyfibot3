import time
import random
import string
from pyfibot.bot.ircbot import IRCbot
from pyfibot.plugin import Plugin


class TestPlugin(Plugin):
    @Plugin.admin_command('long')
    def long(self, sender, message, raw_message):
        ''' Test function to test long messages. To be removed. '''
        length = int(message.strip())
        response = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(length))

        split_response = []
        split_locations = [10, 20, 40, 80, 100, 200, 300, 400, 500, 600]

        for i in range(len(split_locations) - 1):
            if split_locations[i] > len(response):
                break

            split_response.append(response[split_locations[i]:split_locations[i + 1]])

        self.bot.respond(' '.join(split_response), raw_message)

    @Plugin.admin_command('sleep')
    def sleep(self, sender, message, raw_message):
        ''' Test function to test plugins hanging. To be removed. '''
        try:
            sleep_time = int(message)
        except:
            return

        self.bot.respond('Sleeping for %i seconds.' % sleep_time, raw_message)
        time.sleep(sleep_time)
        self.bot.respond('Slept for %i seconds.' % sleep_time, raw_message)

    @Plugin.interval(1)
    def print_tissit(self):
        if not isinstance(self.bot, IRCbot):
            return
        self.bot.respond('TISSIT!', raw_message={'target': '#pyfibot'})

    @Plugin.admin_command('raise_exception')
    def raise_exception(self, sender, message, raw_message):
        raise ValueError('TESTING!')
