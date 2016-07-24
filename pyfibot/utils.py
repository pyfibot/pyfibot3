import math
from datetime import datetime, timedelta, tzinfo
import dateutil.tz
import dateutil.parser


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


def get_duration_string(dt, maximum_elements=2, return_delta=False):
    '''
    Return duration string between two datetimes.

    Argument dt can either be a datetime, timedelta, integer, or float.
    If dt is integer or float, it's considered to be seconds.

    Argument maximum_elements limits the maximum number of returned elements.

    If argument return_delta is True, the actual delta value is sent together with
    the string.
    '''
    if isinstance(dt, timedelta):
        delta = dt.total_seconds()
    elif isinstance(dt, int) or isinstance(dt, float):
        delta = dt
    elif isinstance(dt, datetime):
        if dt.tzinfo is None:
            now = datetime.now()
        else:
            now = get_timezone_datetime(tz=dt.tzinfo)
        delta = (dt - now).total_seconds()

    secs = abs(delta)

    years = secs // 31536000
    secs -= years * 31536000

    days = secs // 86400
    secs -= days * 86400

    hours, minutes, seconds = secs // 3600, secs // 60 % 60, secs % 60

    # TODO: possibly add rounding based on maximum_elements?

    parts = []
    if years:
        parts.append('%dy' % years)
    if days > 0:
        parts.append('%dd' % days)
    if hours > 0:
        parts.append('%dh' % hours)
    if minutes > 0:
        parts.append('%dm' % minutes)
    if int(seconds) > 0:
        parts.append('%ds' % seconds)

    timedelta_string = ' '.join(parts[0:maximum_elements])

    if not return_delta:
        return timedelta_string
    return timedelta_string, delta


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
