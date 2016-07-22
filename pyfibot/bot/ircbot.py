import time
import random
import bottom
from pyfibot.bot import Bot


class IRCbot(Bot):
    ''' Bot implementing IRC protocol. '''
    def __init__(self, core, name):
        super(IRCbot, self).__init__(core, name)
        network_configuration = self.network_configuration

        self.server = network_configuration['server']
        self.port = int(network_configuration.get('port', '6667'))
        self.realname = network_configuration.get('realname') or self.core.realname
        self.channels = [
            IRCChannel(self, channel) if not isinstance(channel, list) else IRCChannel(self, *channel)
            for channel in network_configuration.get('channels', [])
        ]

    def _get_builtin_commands(self):
        commands = super(IRCbot, self)._get_builtin_commands()
        commands.update({
            'join': self.command_join,
        })
        return commands

    def is_admin(self, raw_message):
        identifier = '%s!%s@%s' % (
            raw_message.get('nick'),
            raw_message.get('user'),
            raw_message.get('host')
        )
        return any([admin == identifier for admin in self.admins])

    def connect(self):
        bot = bottom.Client(host=self.server, port=self.port, ssl=False, loop=self.core.loop)

        @bot.on('CLIENT_CONNECT')
        def on_connect(**kwargs):
            bot.send('NICK', nick=self.nickname)
            bot.send('USER', user=self.nickname, realname=self.realname)
            for channel in self.channels:
                channel.join()

        @bot.on('CLIENT_DISCONNECT')
        def on_disconnect(**kwargs):
            sleep_time = random.randrange(5, 15, 1)
            print('%s disconnected. Reconnecting in %i seconds.' % (self.nickname, sleep_time))
            time.sleep(sleep_time)
            self.connect(self.core.loop)

        @bot.on('PING')
        def on_ping(message, **kwargs):
            bot.send('PONG', message=message)

        @bot.on('PRIVMSG')
        def on_privmsg(**raw_message):
            sender = raw_message.get('nick')
            message = raw_message.get('message')
            self.handle_message(sender, message, raw_message=raw_message)

        @bot.on('response')
        def on_respose(message, raw_message):
            nick = raw_message.get('nick')
            target = raw_message.get('target')

            # Don't react to own messages
            if nick == self.nickname:
                return
            if target == self.nickname:
                bot.send('PRIVMSG', target=nick, message=message)
                return
            bot.send('PRIVMSG', target=target, message=message)

        @bot.on('JOIN')
        def on_join(**raw_message):
            channel = self.find_channel(raw_message.get('channel'))
            if not channel:
                return

            nick = raw_message.get('nick')
            if nick == self.nickname:
                channel.on_bot_join(**raw_message)
                return

            channel.on_user_join(**raw_message)

        @bot.on('PART')
        def on_part(**raw_message):
            channel = self.find_channel(raw_message.get('channel'))
            if not channel:
                return

            nick = raw_message.get('nick')
            if nick == self.nickname:
                channel.on_bot_part(**raw_message)
                return

            channel.on_user_part(**raw_message)

        @bot.on('RPL_WHOREPLY')
        def on_rpl_who(**raw_message):
            channel = self.find_channel(raw_message.get('channel'))
            if not channel:
                return

            user = channel.find_user(nick=raw_message.get('nick'))
            if not user:
                channel.users.append(IRCUser(self, **raw_message))
                return

            user.update_information(**raw_message)

        @bot.on('QUIT')
        def on_quit(**raw_message):
            nick = raw_message.get('nick')

            for channel in self.channels:
                channel.on_user_quit(nick)

        self._bot = bot

        return bot.loop.create_task(self._bot.connect())

    def find_channel(self, name):
        ''' Find channel from bot channels. '''
        for channel in self.channels:
            if channel.name == name:
                return channel
        return None

    def command_join(self, bot, sender, message, raw_message):
        ''' Command to join IRC channels. '''
        if not self.is_admin(raw_message):
            return

        existing_channel = self.find_channel(message.split(' ')[0])
        if existing_channel:
            existing_channel.join()
            return

        channel = IRCChannel(self, *message.split(' '))
        channel.join()
        self.channels.append(channel)
    # Set join as admin command.
    command_join._is_admin_command = True

    def respond(self, message, raw_message):
        self._bot.trigger('response', message=self.cleanup_response(message), raw_message=raw_message)


class IRCChannel(object):
    ''' Object to hold information of an IRC channel. '''
    def __init__(self, irc_instance, name, password=None):
        self.irc_instance = irc_instance
        self.name = name
        self.password = password

        self.users = []

    def join(self):
        ''' Join this channel. '''
        if self.password:
            self.irc_instance._bot.send('JOIN', channel=self.name, key=self.password)
        else:
            self.irc_instance._bot.send('JOIN', channel=self.name)

    def on_bot_join(self, **raw_message):
        ''' Callback to call when bot has joined the channel. '''
        print('Joined %s' % (raw_message.get('channel')))
        self.irc_instance._bot.send('WHO', mask=self.name)

    def on_user_join(self, **raw_message):
        ''' Callback to call when an user has joined the channel. '''
        nick = raw_message.get('nick')

        if not nick or self.find_user(nick):
            return

        self.users.append(IRCUser(self.irc_instance, **raw_message))

    def on_bot_part(self, **raw_message):
        ''' Callback to call when bot parts the channel. '''
        print('Parted %s' % (raw_message.get('channel')))
        print(raw_message)

    def on_user_part(self, **raw_message):
        ''' Callback to call when an user parts the channel. '''
        nick = raw_message.get('nick')
        user = self.find_user(nick)
        if not nick or not user:
            return

        self.users.remove(user)

    def on_user_quit(self, nick):
        ''' Callback to call when an user quits. '''
        user = self.find_user(nick)
        if not user:
            return

        self.users.remove(user)

    def find_user(self, nick):
        ''' Find user in channel. '''
        for user in self.users:
            if user.nick == nick:
                return user
        return None


class IRCUser(object):
    ''' Object to hold information of an IRC user. '''
    def __init__(self, irc_instance, **raw_message):
        self.channel_modes = {}
        self.update_information(**raw_message)

    def __repr__(self):
        return '<IRCUser %s!%s@%s>' % (
            '%s' % self.nick,
            self.user,
            self.host
        )

    def update_information(self, **raw_message):
        ''' Update user information from channel activities. '''
        self.nick = raw_message.get('nick')

        self.real_name = raw_message.get('real_name')
        self.user = raw_message.get('user')
        self.host = raw_message.get('host')

        channel = raw_message.get('channel')
        if channel:
            self.channel_modes[channel] = list(raw_message.get('hg_code', ''))

    def is_op(self, channel):
        ''' Check if user is op in channel. '''
        try:
            return '@' in self.channel_modes[channel]
        except KeyError:
            return False
