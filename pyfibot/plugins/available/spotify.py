"""
Parse spotify URLs
"""

from __future__ import unicode_literals, print_function, division
import re
from pyfibot.plugin import Plugin
from pyfibot.url.handlers import spotify


class Spotify(Plugin):
    @Plugin.listener()
    def spotify(self, sender, message, raw_message):
        """Grab Spotify URLs from the messages and handle them"""

        m = re.match(r'.*(spotify:)(?P<item>album|artist|track|user[:\/]\S+[:\/]playlist)[:\/](?P<id>[a-zA-Z0-9]+)\/?.*', message)
        if not m:
            return None

        title = spotify.spotify(self.bot, None, m)
        if title:
            self.bot.respond(title, raw_message)
