# -*- encoding: utf-8 -*-
"""
Get consignment tracking info from Matkahuolto
"""

from pyfibot.plugin import Plugin
from pyfibot.url import URL
from datetime import datetime
from pyfibot.utils import get_relative_time_string


class Matkahuolto(Plugin):
    @Plugin.command('matkahuolto')
    def matkahuolto(self, sender, message, raw_message):
        ''' Get latest consignment status from Matkahuolto Track & Trace service. '''
        params = {'package_code': message}

        url = 'https://www.matkahuolto.fi/%s/seuranta/tilanne/' % self.config.get('language', 'en')

        try:
            bs = URL(url).get_bs(params=params)

            events = bs.select('.events-table table tbody tr')
            if not events:
                alert = bs.select('.tracker-status .alert')[0].get_text(strip=True)
                return self.bot.respond(alert, raw_message)

        except Exception as e:
            self.bot.respond('Error while getting tracking data. Check the tracking ID or try again later.', raw_message)
            raise e

        latest_event = events[0].select('td')

        datestr = latest_event[0].get_text(strip=True)
        status = latest_event[1].get_text(strip=True)
        place = latest_event[2].stripped_strings.next()

        dt = datetime.now() - datetime.strptime(datestr, '%d.%m.%Y, %H:%M')

        return self.bot.respond(' - '.join([get_relative_time_string(dt, lang=self.lang), status, place]), raw_message)
