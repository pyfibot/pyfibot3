from datetime import datetime
import dateutil.tz
import dateutil.parser


def get_utc_datetime():
    ''' Get current time in UTC. '''
    return datetime.now(tz=dateutil.tz.tzutc())


def get_local_datetime():
    ''' Get current time in local timezone. '''
    return datetime.now(tz=dateutil.tz.tzlocal())


def get_timezone_datetime(timezone):
    '''
    Get current time in defined timezone.
        get_timezone_datetime('Europe/Helsinki')
    '''
    return datetime.now(tz=dateutil.tz.gettz(timezone))


def parse_datetime(s):
    ''' Parse datetime from string. '''
    return dateutil.parser.parse(s)
