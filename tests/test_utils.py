from datetime import datetime, timedelta
from dateutil.tz import tzutc, tzlocal, gettz
import pyfibot.utils


def test_get_duration_string():
    values = {
        '30s': 30,
        '1m': 60,
        '7m 10s': 7 * 60 + 10,
        '7h 10s': 7 * 3600 + 10,
        '7h 2m': 7 * 3600 + 120 + 10,
        '31d 2h': 31 * 86400 + 2 * 3600 + 53,
        '182d 2h': 182 * 86400 + 2 * 3600 + 53,
    }

    for string, seconds in values.items():
        assert pyfibot.utils.get_duration_string(seconds) == string
        assert pyfibot.utils.get_duration_string(timedelta(seconds=seconds)) == string
        assert pyfibot.utils.get_duration_string(datetime.now() - timedelta(seconds=seconds)) == string
        assert pyfibot.utils.get_duration_string(datetime.now(tz=tzutc()) - timedelta(seconds=seconds)) == string
        assert pyfibot.utils.get_duration_string(datetime.now(tz=tzlocal()) - timedelta(seconds=seconds)) == string
        assert pyfibot.utils.get_duration_string(datetime.now(tz=gettz('US/Pacific')) - timedelta(seconds=seconds)) == string

    assert pyfibot.utils.get_duration_string(datetime.now(tz=gettz('Europe/Helsinki')) - datetime.now(tz=gettz('Europe/Stockholm'))) == ''


def test_get_relative_time_string():
    assert pyfibot.utils.get_relative_time_string(-30) == '30s ago'
    assert pyfibot.utils.get_relative_time_string(30) == 'in 30s'
    assert pyfibot.utils.get_relative_time_string(30, lang='fi') == '30s päästä'
    assert pyfibot.utils.get_relative_time_string(-30, lang='fi') == '30s sitten'
