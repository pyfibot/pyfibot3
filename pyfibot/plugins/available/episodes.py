from pyfibot.plugin import Plugin
from pyfibot.utils import parse_datetime, get_utc_datetime, get_relative_time_string
from datetime import datetime
import pytvmaze
import tvdb_api
import tvdb_exceptions


class Episodes(Plugin):
    @Plugin.command(['ep', 'maze'])
    def tvmaze(self, sender, message, raw_message):
        ''' Fetch TV episode information from TVmaze.com '''
        try:
            show = pytvmaze.get_show(show_name=message, embed='episodes')
        except pytvmaze.exceptions.ShowNotFound:
            return self.bot.respond('Show "%s" not found.' % message, raw_message)

        if not show.episodes:
            return self.bot.respond('No episodes found for "%s".' % show.name, raw_message)

        next_episode = None
        now = get_utc_datetime()

        # go through the episodes in reverse order
        for episode in reversed(show.episodes):
            # episode has id and name, but no airstamp yet (not announced)
            if not episode.airstamp:
                continue

            # Episode is in the past, stop searching
            if parse_datetime(episode.airstamp) < now:
                break

            # episode is (still) in the future
            next_episode = episode

        if not next_episode:
            next_episode = show.episodes.pop()
            msg = 'Latest episode of "{show_name}" {season:d}x{episode:02d} "{title}" aired on {date} ({relative_date})'
        else:
            msg = 'Next episode of "{show_name}" {season:d}x{episode:02d} "{title}" airs on {date} ({relative_date})'

        next_episode_time = parse_datetime(next_episode.airstamp)
        msg = msg.format(
            show_name=show.name,
            season=next_episode.season_number,
            episode=next_episode.episode_number,
            title=next_episode.title,
            date=next_episode_time.strftime('%Y-%m-%d'),
            relative_date=get_relative_time_string(next_episode_time, no_time=True)
        )

        # Not all shows have network info for some reason
        if show.network:
            msg += ' on %s' % (show.network['name'])

        if show.status == 'Ended':
            msg += ' [ended]'

        self.bot.respond(msg, raw_message)

    @Plugin.command('tvdb')
    def tvdb(self, sender, message, raw_message):
        ''' Fetch TV episode information from thetvdb.com '''

        class SmartUI(tvdb_api.BaseUI):
            ''' Returns the latest series that is actually airing '''
            def selectSeries(self, allSeries):
                t = tvdb_api.Tvdb()
                # reverse order, latest shows first(?)
                for series in reversed(allSeries):
                    # search with ID directly to skip name->ID lookup in library
                    status = t[series['id']].data['status']
                    if status == "Continuing":
                        return series
                if len(allSeries) > 0:
                    return allSeries[0]

        t = tvdb_api.Tvdb(custom_ui=SmartUI)
        now = datetime.now()

        try:
            series = t[message]
        except (TypeError, tvdb_exceptions.tvdb_shownotfound):
            return self.bot.respond('Series "%s" not found' % message, raw_message)

        future_episodes = []
        all_episodes = []

        # find all episodes with airdate > now
        for season_no, season in series.items():
            for episode_no, episode in season.items():
                firstaired = episode['firstaired']
                if not firstaired:
                    continue
                airdate = parse_datetime(firstaired)

                all_episodes.append(episode)
                if airdate > now:
                    future_episodes.append(episode)

        # if any future episodes were found, find out the one with airdate closest to now
        if future_episodes:
            # sort the list just in case it's out of order (specials are season 0)
            future_episodes = sorted(future_episodes, key=lambda x: x['firstaired'])
            episode = future_episodes[0]
            msg = 'Next episode of "{show_name}" {season:d}x{episode:02d} "{title}" airs on {date} ({relative_date})'
        # no future episodes found, show the latest one
        elif all_episodes:
            # find latest episode of the show
            all_episodes = sorted(all_episodes, key=lambda x: x['firstaired'])
            episode = all_episodes[-1]

            msg = 'Latest episode of "{show_name}" {season:d}x{episode:02d} "{title}" aired on {date} ({relative_date})'
        else:
            return self.bot.respond('No episodes found for "%s".' % series.data['seriesname'], raw_message)

        episode_time = parse_datetime(episode['firstaired'])
        msg = msg.format(
            show_name=series.data['seriesname'],
            season=int(episode['combined_season']),
            episode=int(float(episode['combined_episodenumber'])),
            title=episode['episodename'],
            date=episode_time.strftime('%Y-%m-%d'),
            relative_date=get_relative_time_string(episode_time, no_time=True)
        )

        self.bot.respond(msg, raw_message)
