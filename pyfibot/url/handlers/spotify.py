import re
from pyfibot.url import URL, urlhandler


@urlhandler(re.compile(r'((open|play)\.spotify\.com\/)(?P<item>album|artist|track|user[:\/]\S+[:\/]playlist)[:\/](?P<id>[a-zA-Z0-9]+)\/?.*'))
def spotify(bot, url, match):
    spotify_id = match.group('id')
    item = match.group('item').replace(':', '/').split('/')
    item[0] += 's'
    if item[0] == 'users':
        # All playlists seem to return 401 at the time, even the public ones
        return None

    apiurl = "https://api.spotify.com/v1/%s/%s" % ('/'.join(item), spotify_id)
    r = URL.get_url(apiurl)

    if r.status_code != 200:
        if r.status_code not in [401, 403]:
            bot.log.warning('Spotify API returned %s while trying to fetch %s' % r.status_code, apiurl)
        return

    data = r.json()

    title = '[Spotify] '
    if item[0] in ['albums', 'tracks']:
        artists = []
        for artist in data['artists']:
            artists.append(artist['name'])
        title += ', '.join(artists)

    if item[0] == 'albums':
        title += ' - %s (%s)' % (data['name'], data['release_date'])

    if item[0] == 'artists':
        title += data['name']
        genres_n = len(data['genres'])
        if genres_n > 0:
            genitive = 's' if genres_n > 1 else ''
            genres = data['genres'][0:4]
            more = ' +%s more' % genres_n - 5 if genres_n > 4 else ''

            title += ' (Genre%s: %s%s)' % (genitive, ', '.join(genres), more)

    if item[0] == 'tracks':
        title += ' - %s - %s' % (data['album']['name'], data['name'])

    return title
