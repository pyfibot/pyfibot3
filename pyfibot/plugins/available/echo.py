from pyfibot.plugin import Plugin


class Echo(Plugin):
    @Plugin.command('echo')
    def echo(self, sender, message, raw_message):
        self.bot.respond(message, raw_message)
