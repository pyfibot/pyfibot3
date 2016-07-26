# import asyncio


# https://mail.python.org/pipermail/python-list/2013-November/661060.html
# https://mail.python.org/pipermail/python-list/2013-November/661061.html
class PeriodicTask(object):
    def __init__(self, func, interval, bot):
        self._func = func
        self._interval = interval
        self._bot = bot
        self._loop = self._bot.core.loop
        self._set()

    def _set(self):
        self._handler = self._loop.call_later(self._interval, self._run)

    def _run(self):
        self._func(self._bot)
        self._handler = self._loop.call_later(self._interval, self._run)

    def stop(self):
        self._handler.cancel()
