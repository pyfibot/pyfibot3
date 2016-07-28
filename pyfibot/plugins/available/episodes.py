from pyfibot.plugin import Plugin
from pyfibot.utils import parse_datetime, get_timezone_datetime, get_relative_time_string
import pytvmaze


class Episodes(Plugin):
    def init(self):
        self.timezone = self.bot.core.configuration.get('timezone', 'Europe/Helsinki')

    @Plugin.command(['ep', 'maze'])
    def tvmaze(self, sender, message, raw_message):
        ''' Fetch TV episode information from TVmaze.com '''
        try:
            show = pytvmaze.get_show(show_name=message, embed='episodes')
        except pytvmaze.exceptions.ShowNotFound:
            return self.bot.respond('Show "%s" not found.' % message, raw_message)

        if not show.episodes:
            return self.bot.respond('No new episodes found for "%s".' % show.name, raw_message)

        next_episode = None
        now = get_timezone_datetime(self.timezone)

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
            relative_date=get_relative_time_string(next_episode_time)
        )

        # Not all shows have network info for some reason
        if show.network:
            msg += ' on %s' % (show.network['name'])

        if show.status == 'Ended':
            msg += ' [ended]'

        self.bot.respond(msg, raw_message)
