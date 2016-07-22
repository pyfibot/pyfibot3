import random
import string
from pyfibot.decorators import admin_command


@admin_command('long')
def long(bot, sender, message, message_arguments):
    ''' Test function to test long messages. To be removed. '''
    length = int(message.strip())
    response = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(length))

    split_response = []
    split_locations = [10, 20, 40, 80, 100, 200, 300, 400, 500, 600]
    for i in range(len(split_locations) - 1):
        if split_locations[i] > len(response):
            break

        split_response.append(response[split_locations[i]:split_locations[i + 1]])
    bot.respond(' '.join(split_response), message_arguments)
