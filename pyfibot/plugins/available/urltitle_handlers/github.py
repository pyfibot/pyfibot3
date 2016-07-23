from pyfibot.decorators import urlhandler


@urlhandler('github.com/*')
def github(bot, url):
    # Don't react to Github -urls, as the url itself is enough.
    return False
