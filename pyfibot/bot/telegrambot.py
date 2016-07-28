import aiotg
from pyfibot.bot import Bot
from pyfibot.utils import datetime_fromtimestamp, get_duration_string


class TelegramBot(Bot):
    ''' Bot implementing IRC protocol. '''
    def __init__(self, core, name):
        super(TelegramBot, self).__init__(core, name)
        self.api_token = self.configuration.get('api_token')
        self.message_timeout = self.configuration.get('message_timeout', 15)

        if not self.api_token:
            raise AttributeError('TelegramBot API key not found!')

    def _get_builtin_commands(self):
        commands = super(TelegramBot, self)._get_builtin_commands()
        commands.update({
            'get_user_id': self.command_get_user_id,
        })
        return commands

    def is_admin(self, raw_message):
        for admin in self.admins:
            try:
                if raw_message['chat'].sender.get('id', '-1') == int(admin):
                    return True
            except:
                continue
        return False

    def connect(self):
        bot = aiotg.Bot(api_token=self.api_token)

        @bot.command(r'(.+)')
        def handle_message(chat, match):
            sender = chat.sender.get('id') or chat.sender.get('first_name', '')
            _, delta = get_duration_string(datetime_fromtimestamp(chat.message.get('date'), 'UTC'), return_delta=True)

            # Only handle messages newer than message timeout
            if abs(delta) > self.message_timeout:
                return

            message = match.group(1)
            raw_message = {
                'chat': chat,
                'match': match
            }

            self.handle_message(sender, message, raw_message=raw_message)

        self._bot = bot
        task = self.core.loop.create_task(self._bot.loop())
        task.add_done_callback(self.reconnect)

    def respond(self, message, raw_message):
        chat = raw_message.get('chat')
        if not chat:
            return
        self.core.loop.create_task(
            self._bot.send_message(
                chat.id,
                message,
                **raw_message.get('telegram_options', {})
            )
        )

    def command_get_user_id(self, sender, message, raw_message):
        ''' Get user ID for Telegram user. '''
        self.respond(sender, raw_message)
