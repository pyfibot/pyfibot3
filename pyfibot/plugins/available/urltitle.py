from pyfibot.url import URL
from pyfibot.decorators import init, listener


@init
def init_urltitle(bot):
    global check_reduntant
    URL.discover_handlers()
    check_reduntant = bot.core_configuration.get('urltitle', {}).get('check_reduntant', False)


@listener
def print_titles(bot, sender, message, raw_message):
    urls = URL.get_urls(message)
    if not urls or len(urls) > 3:
        # Do nothing, if urls are not found or number of urls is large.
        return

    for url in urls:
        title = url.get_title(bot, check_reduntant=check_reduntant)

        if title is False:
            print('Title returned as False -> not printing.')
            return

        if isinstance(title, str):
            return bot.respond('Title: %s' % title, raw_message)

    return bot.respond('Detected %i urls.' % len(urls), raw_message)
