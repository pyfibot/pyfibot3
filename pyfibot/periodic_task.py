import sys
from pyfibot.coloredlogger import ColoredLogger


# https://mail.python.org/pipermail/python-list/2013-November/661060.html
# https://mail.python.org/pipermail/python-list/2013-November/661061.html
class PeriodicTask(object):
    def __init__(self, func, interval, bot):
        self._func = func
        self._interval = interval
        self._bot = bot
        self._loop = self._bot.core.loop
        self._set()

    @property
    def log(self):
        return ColoredLogger(self.__class__.__name__)

    def _set(self):
        self._handler = self._loop.call_later(
            self._interval,
            self._bot.core.loop.run_in_executor, None, self._run
        )

    def _run(self):
        try:
            self._func(self._bot)
        except:
            self.log.error('Error running task.', exc_info=sys.exc_info())
        self._set()

    def stop(self):
        self._handler.cancel()
