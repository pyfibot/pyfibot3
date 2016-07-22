import time
from pyfibot.decorators import command


@command('sleep')
def sleep(bot, sender, message, message_arguments):
    ''' Test function to test plugins hanging. To be removed. '''
    try:
        sleep_time = int(message)
    except:
        return
    time.sleep(sleep_time)
    bot.respond('Slept for %i seconds.' % sleep_time, message_arguments)
