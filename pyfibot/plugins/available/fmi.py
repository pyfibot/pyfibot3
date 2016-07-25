# -*- encoding: utf-8 -*-
from datetime import datetime, timedelta
from math import isnan
from pyfibot.decorators import command, init

TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'


@init
def init_fmi(bot):
    global default_place
    default_place = bot.core_configuration.get('plugin_fmi', {}).get('default_place', 'Helsinki')


@command(['sää', 'saa', 'fmi'])
def command_fmi(bot, sender, message, raw_message):
    ''' Fetch weather information from Finnish Meteorological Institute. '''
    if message:
        place = message
    else:
        global default_place
        place = default_place

    starttime = (datetime.utcnow() - timedelta(minutes=10)).strftime(TIME_FORMAT) + 'Z'
    params = {
        'request': 'getFeature',
        'storedquery_id': 'fmi::observations::weather::timevaluepair',
        'parameters': ','.join(['t2m', 'ws_10min', 'rh', 'n_man', 'wawa']),
        'crs': 'EPSG::3067',
        'place': place,
        'maxlocations': 1,
        'starttime': starttime
    }

    bs = bot.get_bs('http://data.fmi.fi/fmi-apikey/%s/wfs' % 'c86a0cb3-e0bf-4604-bfe9-de3ca92e0afc', params=params)

    # Get FMI name, gives the observation place more accurately
    try:
        place = bs.find('gml:name').text
    except AttributeError:
        return bot.respond('Paikkaa ei löytynyt.', raw_message)

    # Loop through measurement time series -objects and gather values
    values = {}
    for mts in bs.find_all('wml2:measurementtimeseries'):
        # Get the identifier from mts-tag
        target = mts['gml:id'].split('-')[-1]
        # Get last value from measurements (always sorted by time)
        value = float(mts.find_all('wml2:value')[-1].text)
        # NaN is returned, if observation doesn't exist
        if not isnan(value):
            values[target] = value

    # Build text from values found
    text = []
    if 't2m' in values:
        text.append('lämpötila: %.1f°C' % values['t2m'])
    if 't2m' in values and 'ws_10min' in values:
        # Calculate "feels like" if both temperature and wind speed were found
        feels_like = 13.12 + 0.6215 * values['t2m'] \
            - 13.956 * (values['ws_10min'] ** 0.16) \
            + 0.4867 * values['t2m'] * (values['ws_10min'] ** 0.16)
        text.append('tuntuu kuin: %.1f°C' % feels_like)
    if 'ws_10min' in values:
        text.append('tuulen nopeus: %i m/s' % round(values['ws_10min']))
    if 'rh' in values:
        text.append('ilman kosteus: %i%%' % round(values['rh']))
    if 'n_man' in values:
        text.append('pilvisyys: %i/8' % int(values['n_man']))

    # Return place and values to the channel
    bot.respond('%s: %s' % (place, ', '.join(text)), raw_message)
