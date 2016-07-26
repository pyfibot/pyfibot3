from pyfibot.url import URL
from pyfibot.plugin import Plugin


class URLtitle(Plugin):
    def init(self):
        self.check_reduntant = self.config.get('check_reduntant', False)

    @Plugin.listener()
    def print_titles(self, sender, message, raw_message):
        urls = URL.get_urls(message)
        if not urls or len(urls) > 3:
            # Do nothing, if urls are not found or number of urls is large.
            return

        for url in urls:
            title = url.get_title(self.bot, check_reduntant=self.check_reduntant)

            if title is False:
                print('Title returned as False -> not printing.')
                return

            if isinstance(title, str):
                return self.bot.respond('Title: %s' % title, raw_message)

        return self.bot.respond('Detected %i urls.' % len(urls), raw_message)
