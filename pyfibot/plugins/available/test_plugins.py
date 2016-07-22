import time
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


@admin_command('sleep')
def sleep(bot, sender, message, message_arguments):
    ''' Test function to test plugins hanging. To be removed. '''
    try:
        sleep_time = int(message)
    except:
        return

    bot.respond('Sleeping for %i seconds.' % sleep_time, message_arguments)
    time.sleep(sleep_time)
    bot.respond('Slept for %i seconds.' % sleep_time, message_arguments)
