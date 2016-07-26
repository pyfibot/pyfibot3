from pyfibot.plugin import Plugin
from pyfibot.utils import get_timezone_datetime, parse_datetime


class Skinfo(Plugin):
    def _fetch_restaurant(self, restaurant):
        response = self.bot.get_url('http://skinfo.dy.fi/api/complete.json')
        if response.status_code != 200:
            return 'Skinfo alhaalla?'

        json = response.json()

        now = get_timezone_datetime('Europe/Helsinki')
        for date, data in json.get('restaurants', {}).get(restaurant, {}).get('days', {}).items():
            closing_time = data.get('lunch_times', {}).get('end', '')

            if not closing_time:
                continue

            closing_time = parse_datetime(closing_time)
            if closing_time < now:
                continue

            foods = data.get('foods', [])
            if not foods:
                continue

            return '%s | %s' % (
                closing_time.strftime('%d.%m.'),
                ' | '.join([
                    food['title_fi'] for food in foods
                ])
            )

        return 'Ruokaa ei löytynyt :('

    @Plugin.command('kurnis')
    def kurniekka(self, sender, message, raw_message):
        ''' Fetch menu from Kurniekka. '''
        self.bot.respond(self._fetch_restaurant('laseri'), raw_message)
