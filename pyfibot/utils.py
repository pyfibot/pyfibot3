from datetime import datetime
import dateutil.tz
import dateutil.parser


def get_utc_datetime():
    return datetime.now(tz=dateutil.tz.tzutc())


def get_local_datetime():
    return datetime.now(tz=dateutil.tz.tzlocal())


def get_timezone_datetime(timezone):
    return datetime.now(tz=dateutil.tz.gettz(timezone))


def parse_datetime(s):
    return dateutil.parser.parse(s)
