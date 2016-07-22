"""
Get shipment tracking info from Posti
"""

from pyfibot.decorators import init, command
from pyfibot.utils import parse_datetime, get_relative_time_string
from urllib.parse import quote_plus


@init
def init(bot):
    global lang
    lang = bot.core_configuration.get('plugin_posti', {}).get('language', 'en')


@command('posti')
def posti(bot, sender, message, raw_message):
    ''' Get latest tracking event for a shipment from Posti. Usage: .posti JJFI00000000000000 '''

    if not message:
        return bot.respond('Tracking ID is required.', raw_message)

    url = 'http://www.posti.fi/henkiloasiakkaat/seuranta/api/shipments/%s' % quote_plus(message)

    try:
        r = bot.get_url(url)
        r.raise_for_status()
        data = r.json()
        shipment = data['shipments'][0]
    except Exception:
        return bot.respond('Error while getting tracking data. Check the tracking ID or try again later.', raw_message)

    phase = shipment['phase']
    eta_timestamp = shipment.get('estimatedDeliveryTime')
    latest_event = shipment['events'][0]

    event_time = get_relative_time_string(parse_datetime(latest_event['timestamp']), lang=lang)
    description = latest_event['description'][lang]
    location = '%s %s' % (latest_event['locationCode'], latest_event['locationName'])

    msg = ' - '.join([event_time, description, location])

    if phase != 'DELIVERED' and eta_timestamp:
        eta_dt = parse_datetime(eta_timestamp)
        eta_txt = eta_dt.strftime('%d.%m.%Y %H:%M')
        msg = 'ETA %s - %s' % (eta_txt, msg)

    bot.respond(msg, raw_message)
