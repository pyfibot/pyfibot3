import math
from datetime import datetime, timedelta, tzinfo
import dateutil.tz
import dateutil.parser
from dateutil.relativedelta import relativedelta


def get_utc_datetime():
    ''' Get current time in UTC. '''
    return datetime.now(tz=dateutil.tz.tzutc())


def get_local_datetime():
    ''' Get current time in local timezone. '''
    return datetime.now(tz=dateutil.tz.tzlocal())


def get_timezone_datetime(tz):
    '''
    Get current time in defined timezone.
        get_timezone_datetime('Europe/Helsinki')
    '''
    if isinstance(tz, tzinfo):
        return datetime.now(tz=tz)

    return datetime.now(tz=dateutil.tz.gettz(tz))


def parse_datetime(s):
    ''' Parse datetime from string. '''
    return dateutil.parser.parse(s)


def datetime_fromtimestamp(timestamp, tz=None):
    if tz is None:
        return datetime.fromtimestamp(timestamp)
    return datetime.fromtimestamp(timestamp, tz=dateutil.tz.gettz(tz))


def get_duration_string(dt, maximum_elements=2, return_delta=False):
    '''
    Return duration string between two datetimes.

    Argument dt can either be a datetime, timedelta, relativedelta, integer, or float.
    If dt is integer or float, it's considered to be seconds.

    Argument maximum_elements limits the maximum number of returned elements.

    If argument return_delta is True, the number of seconds is sent together with
    the string.
    '''

    if isinstance(dt, relativedelta):
        delta = dt
    elif isinstance(dt, timedelta):
        delta = relativedelta(seconds=dt.total_seconds())
    elif isinstance(dt, int) or isinstance(dt, float):
        delta = relativedelta(seconds=dt)
    elif isinstance(dt, datetime):
        # Need to hack a bit, as relativedeltas taken between two dates are represented with
        # years, months etc, while ones from seconds are not... And yes, even after .normalized()
        if dt.tzinfo is None:
            delta = relativedelta(seconds=(dt - datetime.now()).total_seconds())
        else:
            delta = relativedelta(seconds=(dt - get_timezone_datetime(tz=dt.tzinfo)).total_seconds())
    else:
        raise ValueError('Unsupported type for argument dt.')

    delta = delta.normalized()

    # HACK HACK HACK!
    # -25 // 365 == -1
    # -(25 // 365) == 0
    years = delta.days // 365 if delta.days > 0 else -(-delta.days // 365)
    delta = delta - relativedelta(days=years * 365)

    #
    # TODO: possibly add rounding based on maximum_elements?
    #

    parts = []
    if years:
        parts.append('%dy' % abs(years))
    if delta.days:
        parts.append('%dd' % abs(delta.days))
    if delta.hours:
        parts.append('%dh' % abs(delta.hours))
    if delta.minutes:
        parts.append('%dm' % abs(delta.minutes))
    if delta.seconds:
        parts.append('%ds' % abs(delta.seconds))

    timedelta_string = ' '.join(parts[0:maximum_elements])

    if not return_delta:
        return timedelta_string
    return timedelta_string, int(years * 365 * 86400 + delta.days * 86400 + delta.hours * 3600 + delta.seconds)


def get_relative_time_string(dt, maximum_elements=2, lang='en'):
    '''
    Return relative time as string with the proper pre/suffix.
    See get_duration_string documentation for dt and maximum_elements.
    '''
    string_formats = {
        'en': {
            'ago': '%s ago',
            'in': 'in %s',
        },
        'fi': {
            'ago': '%s sitten',
            'in': '%s päästä',
        },
    }

    timedelta_string, delta = get_duration_string(dt, maximum_elements=maximum_elements, return_delta=True)
    if not timedelta_string:
        return None

    if delta < 0:
        return string_formats.get(lang, string_formats['en']).get('ago') % timedelta_string
    return string_formats.get(lang, string_formats['en']).get('in') % timedelta_string


def get_views_string(views):
    views = int(views)

    if views == 0:
        return '0'

    try:
        millnames = ['', 'k', 'M', 'Billion', 'Trillion']
        millidx = max(0, min(len(millnames) - 1, int(math.floor(math.log10(abs(views)) / 3.0))))
        return '%.0f%s' % (views / 10 ** (3 * millidx), millnames[millidx])
    except ValueError:
        return '0'
