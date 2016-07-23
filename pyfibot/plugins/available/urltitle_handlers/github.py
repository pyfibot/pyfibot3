from pyfibot.decorators import urlhandler


@urlhandler('github.com/*')
def github(url):
    return False
