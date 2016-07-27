import re
from pyfibot.url import URL, urlhandler
from datetime import timedelta
from pyfibot.utils import get_utc_datetime, parse_datetime, get_duration_string, get_relative_time_string


@urlhandler('areena.yle.fi/*')
def yle_areena(bot, url):
    """http://areena.yle.fi/*"""
    def _parse_publication_events(data):
        '''
        Parses publication events from the data.
        Returns:
            - ScheduledTransmission
            - OnDemandPublication
            - first broadcast time (or if in the future, the start of availability on-demand) [datetime]
            - the exit time of the on-demand [datetime]
        '''
        now = get_utc_datetime()

        # Finds all publicationEvents from the data.
        publicationEvents = data.get('publicationEvent', [])

        # Finds the scheduled transmissions
        ScheduledTransmission = [event for event in publicationEvents if event.get('type') == 'ScheduledTransmission']
        if ScheduledTransmission:
            # If transmissions are found, use the first one
            ScheduledTransmission = ScheduledTransmission[0]

        # Finds the on-demand transmissions
        OnDemandPublication = [
            event
            for event in publicationEvents
            if event.get('temporalStatus') == 'currently' and event.get('type') == 'OnDemandPublication'
        ]
        if OnDemandPublication:
            # If transmissions are found, use the first one
            OnDemandPublication = OnDemandPublication[0]

        # Find the broadcast time of the transmission
        # First, try to get the time when the on-demand was added to Areena.
        broadcasted = parse_datetime(OnDemandPublication['startTime']) if OnDemandPublication and 'startTime' in OnDemandPublication else None
        if broadcasted is None or broadcasted > now:
            # If on-demand wasn't found, fall back to the scheduled transmission.
            broadcasted = parse_datetime(ScheduledTransmission['startTime']) if ScheduledTransmission and 'startTime' in ScheduledTransmission else None

        # Find the exit time of the on-demand publication
        exits = None
        if OnDemandPublication and 'endTime' in OnDemandPublication:
            exits = parse_datetime(OnDemandPublication['endTime'])

        return ScheduledTransmission, OnDemandPublication, broadcasted, exits

    def get_duration(event):
        ''' Parses duration of an event, returns integer value in seconds. '''
        if not event:
            return

        duration = event.get('duration') or event.get('media', {}).get('duration')
        if duration is None:
            return

        match = re.match(r'P((\d+)Y)?((\d+)D)?T?((\d+)H)?((\d+)M)?((\d+)S)?', duration)
        if not match:
            return

        # Get match group values, defaulting to 0
        match_groups = match.groups(0)

        # Kind of ugly, but works...
        secs = 0
        secs += int(match_groups[1]) * 365 * 86400
        secs += int(match_groups[3]) * 86400
        secs += int(match_groups[5]) * 3600
        secs += int(match_groups[7]) * 60
        secs += int(match_groups[9])
        return secs

    def get_episode(identifier):
        ''' Gets episode information from Areena '''
        api_url = 'https://external.api.yle.fi/v1/programs/items/%s.json' % (identifier)
        params = {
            'app_id': bot.core_configuration.get('urltitle', {}).get('areena', {}).get('app_id', 'cd556936'),
            'app_key': bot.core_configuration.get('urltitle', {}).get('areena', {}).get('app_key', '25a08bbaa8101cca1bf0d1879bb13012'),
        }
        data = URL(api_url).get_json(params=params)
        if not data:
            return

        data = data.get('data', None)
        if not data:
            return

        title = data.get('title', {}).get('fi', None)
        if not title:
            return

        episode_number = data.get('episodeNumber', -100)
        season_number = data.get('partOfSeason', {}).get('seasonNumber', -100)

        if episode_number != -100 and season_number != -100:
            title += ' - %dx%02d' % (season_number, episode_number)

        promotionTitle = data.get('promotionTitle', {}).get('fi')
        if promotionTitle:
            title += ' - %s' % promotionTitle

        duration = get_duration(data)

        _, OnDemandPublication, broadcasted, exits = _parse_publication_events(data)

        title_data = []
        if duration:
            title_data.append(get_duration_string(duration))
        if broadcasted:
            title_data.append(get_relative_time_string(broadcasted, lang='en'))
        if exits and get_utc_datetime() + timedelta(days=2 * 365) > exits:
            title_data.append('exits %s' % get_relative_time_string(exits, maximum_elements=1))
        if not OnDemandPublication:
            title_data.append('not available')
        return '%s [%s]' % (title, ' - '.join(title_data))

    def get_series(identifier):
        ''' Gets series information from Areena '''
        api_url = 'https://external.api.yle.fi/v1/programs/items.json'
        params = {
            'app_id': bot.core_configuration.get('urltitle', {}).get('areena', {}).get('app_id', 'cd556936'),
            'app_key': bot.core_configuration.get('urltitle', {}).get('areena', {}).get('app_key', '25a08bbaa8101cca1bf0d1879bb13012'),
            'series': identifier,
            'order': 'publication.starttime:desc',
            'availability': 'ondemand',
            'type': 'program',
            'limit': 100,
        }

        data = URL(api_url).get_json(params=params)
        if not data:
            return

        data = data.get('data', None)
        if not data:
            return

        latest_episode = data[0]
        title = latest_episode.get('title', {}).get('fi', None)
        if not title:
            return

        _, _, broadcasted, _ = _parse_publication_events(latest_episode)

        title_data = ['SERIES']
        if len(data) >= 100:
            title_data.append('100+ episodes')
        else:
            title_data.append('%i episodes' % len(data))
        if broadcasted:
            title_data.append('latest episode: %s' % get_relative_time_string(broadcasted))

        return '%s [%s]' % (title, ' - '.join(title_data))

    # There's still no endpoint to fetch the currently playing shows via API :(
    if 'suora' in url.url:
        bs = URL(url.url).get_bs()
        if not bs:
            return
        container = bs.find('div', {'class': 'selected'})
        channel = container.find('h3').text
        try:
            program = container.find('li', {'class': 'current-broadcast'}).find('div', {'class': 'program-title'})
        except AttributeError:
            return '%s (LIVE)' % (channel)

        link = program.find('a').get('href', None)
        if not link:
            return '%s - %s (LIVE)' % (channel, program.text.strip())
        return '%s - %s <http://areena.yle.fi/%s> (LIVE)' % (channel, program.text.strip(), link.lstrip('/'))

    try:
        identifier = url.path.split('/')[-1]
    except:
        bot.log.debug('Areena identifier could not be found.')
        return

    # Try to get the episode (preferred) or series information from Areena
    return get_episode(identifier) or get_series(identifier)
