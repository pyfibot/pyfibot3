from pyfibot.decorators import urlhandler
from pyfibot.utils import get_views_string


@urlhandler('imdb.com/title/tt*')
def imdb(bot, url):
    imdb_id = [x for x in url.path.split('/') if x][-1]
    if not imdb_id:
        return

    r = bot.get_url('http://www.omdbapi.com/', params={'i': imdb_id})
    data = r.json()

    name = data['Title']
    year = data['Year']
    rating = data['imdbRating']
    votes = data['imdbVotes'].replace(',', '')
    genre = data['Genre'].lower()

    title = '%s (%s) - %s/10 (%s votes) - %s' % (name, year, rating, get_views_string(votes), genre)

    return title
