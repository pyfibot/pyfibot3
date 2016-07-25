# -*- coding: utf-8 -*-
# import logging
from datetime import date, datetime, timedelta
from pyfibot.decorators import command, init


# log = logging.getLogger('openweather')
# default_location = 'Helsinki'
# threshold = 120

# appid = None

@init
def init_openweathermap(bot):
    global appid
    global default_location
    global threshold

    config = bot.core_configuration.get('plugin_openweathermap', {})
    default_location = config.get('default_location', 'Helsinki')
    # log.info('Using %s as default location' % default_location)

    appid = config.get('appid')
    if not appid:
        raise AttributeError('App ID not set.')

    threshold = int(config.get('threshold', 120))  # threshold to show measuring time in minutes


@command(['weather'])
def command_openweathermap(bot, sender, message, raw_message):
    ''' Fetch weather information from OpenWeatherMap. '''
    if not appid:
        # log.warn("No OpenWeatherMap appid set in configuration")
        return False

    if message:
        location = message
    else:
        location = default_location

    url = 'http://api.openweathermap.org/data/2.5/weather?q=%s&units=metric&appid=%s'
    r = bot.get_url(url % (location, appid))

    try:
        data = r.json()
    except:
        # log.debug("Couldn't parse JSON.")
        return bot.respond('Error: API error, unable to parse JSON response.', raw_message)

    if 'cod' not in data or int(data['cod']) != 200:
        # log.debug('status != 200')
        return bot.respond('Error: API error.', raw_message)

    if 'name' not in data:
        return bot.respond('Error: Location not found.', raw_message)
    if 'main' not in data:
        return bot.respond('Error: Unknown error.', raw_message)

    location = '%s, %s' % (data['name'], data['sys']['country'])
    main = data['main']

    if 'temp' not in main:
        return bot.respond('Error: Data not found.', raw_message)

    prefix = '%s' % location

    if 'dt' in data:
        measured = datetime.utcfromtimestamp(data['dt'])
        if datetime.utcnow() - timedelta(minutes=threshold) > measured:
            prefix = '%s (%s UTC)' % (location, measured.strftime('%Y-%m-%d %H:%M'))

    measurement = [
        'Temperature: %.1f°C' % main['temp'],
    ]

    if 'wind' in data and 'speed' in data['wind']:
        wind = data['wind']['speed']  # Wind speed in mps (m/s)

        feels_like = 13.12 + 0.6215 * main['temp'] - 13.956 * (wind ** 0.16) + 0.4867 * main['temp'] * (wind ** 0.16)
        measurement.append('feels like: %.1f°C' % feels_like)
        measurement.append('wind: %.1f m/s' % wind)

    if 'humidity' in main:
        humidity = main['humidity']  # Humidity in %
        measurement.append('humidity: %d%%' % humidity)
    if 'pressure' in main:
        pressure = main['pressure']  # Atmospheric pressure in hPa
        measurement.append('pressure: %d hPa' % pressure)
    if 'clouds' in data and 'all' in data['clouds']:
        cloudiness = data['clouds']['all']  # Cloudiness in %
        measurement.append('cloudiness: %d%%' % cloudiness)

    return bot.respond('%s: %s' % (prefix, ', '.join(measurement)), raw_message)


@command('forecast')
def command_forecast(bot, sender, message, raw_message):
    ''' Fetch weather forecast from OpenWeatherMap. '''
    if message:
        location = message
    else:
        location = default_location

    url = 'http://api.openweathermap.org/data/2.5/forecast/daily?q=%s&cnt=5&mode=json&units=metric&appid=%s'
    r = bot.get_url(url % (location, appid))

    try:
        data = r.json()
    except:
        # log.debug("Couldn't parse JSON.")
        return bot.respond('Error: API error, unable to parse JSON response.', raw_message)

    if 'cod' not in data or int(data['cod']) != 200:
        # log.debug('status != 200')
        return bot.respond('Error: API error.', raw_message)

    if 'city' not in data or 'name' not in data['city']:
        return bot.respond('Error: Location not found.', raw_message)

    if not data['list']:
        return bot.respond('Error: No forecast data.', raw_message)

    prefix = '%s, %s' % (data['city']['name'], data['city']['country'])

    cur_date = date.today()
    forecast_text = []
    for d in data['list']:
        forecast_date = date.fromtimestamp(d['dt'])
        date_delta = (forecast_date - cur_date).days

        if date_delta < 1:
            continue

        if date_delta == 1:
            forecast_text.append('tomorrow: %.1f - %.1f °C (%s)' % (
                d['temp']['min'],
                d['temp']['max'],
                d['weather'][0]['description']
            ))
        else:
            forecast_text.append('in %d days: %.1f - %.1f °C (%s)' % (
                date_delta,
                d['temp']['min'],
                d['temp']['max'],
                d['weather'][0]['description']
            ))

        if len(forecast_text) >= 3:
            break

    return bot.respond('%s: %s' % (prefix, ', '.join(forecast_text)), raw_message)
