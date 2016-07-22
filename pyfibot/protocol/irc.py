import time
import random
import bottom
from .protocol import Protocol


class IRC(Protocol):
    ''' Bot implementing IRC protocol. '''
    def __init__(self, core, name):
        super(IRC, self).__init__(core, name)
        network_configuration = self.network_configuration

        self.server = network_configuration['server']
        self.port = int(network_configuration.get('port', '6667'))
        self.realname = network_configuration.get('realname') or self.core.realname
        self.channels = [
            IRCChannel(self, channel) if not isinstance(channel, list) else IRCChannel(self, *channel)
            for channel in network_configuration.get('channels', [])
        ]

    def _get_builtin_commands(self):
        commands = super(IRC, self)._get_builtin_commands()
        commands.update({
            'join': self.command_join,
        })
        return commands

    def is_admin(self, message_arguments):
        identifier = '%s!%s@%s' % (
            message_arguments.get('nick'),
            message_arguments.get('user'),
            message_arguments.get('host')
        )
        return any([admin == identifier for admin in self.admins])

    def connect(self, loop):
        bot = bottom.Client(host=self.server, port=self.port, ssl=False, loop=loop)

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
            self.connect(loop)

        @bot.on('PING')
        def on_ping(message, **kwargs):
            bot.send('PONG', message=message)

        @bot.on('PRIVMSG')
        def on_privmsg(**message_arguments):
            sender = message_arguments.get('nick')
            message = message_arguments.get('message')
            self.handle_message(sender, message, message_arguments=message_arguments)

        @bot.on('response')
        def on_respose(message, message_arguments):
            nick = message_arguments.get('nick')
            target = message_arguments.get('target')

            # Don't react to own messages
            if nick == self.nickname:
                return
            if target == self.nickname:
                bot.send('PRIVMSG', target=nick, message=message)
                return
            bot.send('PRIVMSG', target=target, message=message)

        @bot.on('JOIN')
        def on_join(**message_arguments):
            channel = self.find_channel(message_arguments.get('channel'))
            if not channel:
                return

            nick = message_arguments.get('nick')
            if nick == self.nickname:
                channel.on_bot_join(**message_arguments)
                return

            channel.on_user_join(**message_arguments)

        @bot.on('PART')
        def on_part(**message_arguments):
            channel = self.find_channel(message_arguments.get('channel'))
            if not channel:
                return

            nick = message_arguments.get('nick')
            if nick == self.nickname:
                channel.on_bot_part(**message_arguments)
                return

            channel.on_user_part(**message_arguments)

        @bot.on('RPL_WHOREPLY')
        def on_rpl_who(**message_arguments):
            channel = self.find_channel(message_arguments.get('channel'))
            if not channel:
                return

            user = channel.find_user(nick=message_arguments.get('nick'))
            if not user:
                channel.users.append(IRCUser(self, **message_arguments))
                return

            user.update_information(**message_arguments)

        @bot.on('QUIT')
        def on_quit(**message_arguments):
            nick = message_arguments.get('nick')

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

    def command_join(self, bot, sender, message, message_arguments):
        ''' Command to join IRC channels. '''
        if not self.is_admin(message_arguments):
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

    def respond(self, message, message_arguments):
        self._bot.trigger('response', message=self.cleanup_response(message), message_arguments=message_arguments)


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

    def on_bot_join(self, **message_arguments):
        ''' Callback to call when bot has joined the channel. '''
        print('Joined %s' % (message_arguments.get('channel')))
        self.irc_instance._bot.send('WHO', mask=self.name)

    def on_user_join(self, **message_arguments):
        ''' Callback to call when an user has joined the channel. '''
        nick = message_arguments.get('nick')

        if not nick or self.find_user(nick):
            return

        self.users.append(IRCUser(self.irc_instance, **message_arguments))

    def on_bot_part(self, **message_arguments):
        ''' Callback to call when bot parts the channel. '''
        print('Parted %s' % (message_arguments.get('channel')))
        print(message_arguments)

    def on_user_part(self, **message_arguments):
        ''' Callback to call when an user parts the channel. '''
        nick = message_arguments.get('nick')
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
    def __init__(self, irc_instance, **message_arguments):
        self.channel_modes = {}
        self.update_information(**message_arguments)

    def __repr__(self):
        return '<IRCUser %s!%s@%s>' % (
            '%s' % self.nick,
            self.user,
            self.host
        )

    def update_information(self, **message_arguments):
        ''' Update user information from channel activities. '''
        self.nick = message_arguments.get('nick')

        self.real_name = message_arguments.get('real_name')
        self.user = message_arguments.get('user')
        self.host = message_arguments.get('host')

        channel = message_arguments.get('channel')
        if channel:
            self.channel_modes[channel] = list(message_arguments.get('hg_code', ''))

    def is_op(self, channel):
        ''' Check if user is op in channel. '''
        try:
            return '@' in self.channel_modes[channel]
        except KeyError:
            return False
