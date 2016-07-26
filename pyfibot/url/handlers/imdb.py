import re
from pyfibot.url import urlhandler
from pyfibot.utils import get_views_string


@urlhandler(re.compile(r'imdb\.com/title/(?P<imdb_id>tt[0-9]+)/?'))
def imdb(bot, url, match):
    r = bot.get_url('http://www.omdbapi.com/', params={'i': match.group('imdb_id')})
    data = r.json()

    name = data['Title']
    year = data['Year']
    rating = data['imdbRating']
    votes = data['imdbVotes'].replace(',', '')
    genre = data['Genre'].lower()

    title = '%s (%s) - %s/10 (%s votes) - %s' % (name, year, rating, get_views_string(votes), genre)

    return title
