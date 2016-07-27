import re
from pyfibot.url import URL, urlhandler
from pyfibot.utils import get_views_string


@urlhandler(re.compile(r'imdb\.com/title/(?P<imdb_id>tt[0-9]+)/?'))
def imdb(bot, url, match):
    data = URL.get_json('http://www.omdbapi.com/', params={'i': match.group('imdb_id')})
    if not data:
        bot.log.error('Failed to fetch IMDB ID "%s"' % match.group('imdb_id'))
        return

    name = data['Title']
    year = data['Year']
    rating = data['imdbRating']
    votes = data['imdbVotes'].replace(',', '')
    genre = data['Genre'].lower()

    title = '%s (%s) - %s/10 (%s votes) - %s' % (name, year, rating, get_views_string(votes), genre)

    return title
