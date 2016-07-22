from pyfibot.decorators import command
from pyfibot.utils import get_timezone_datetime, parse_datetime


def _fetch_restaurant(bot, restaurant):
    response = bot.get_url('http://skinfo.dy.fi/api/complete.json')
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


@command('kurnis')
def kurniekka(bot, sender, message, raw_message):
    ''' Fetch menu from Kurniekka. '''
    bot.respond(_fetch_restaurant(bot, 'laseri'), raw_message)
