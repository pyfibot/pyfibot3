import traceback


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
        self._handler = self._loop.call_later(
            self._interval,
            self._bot.core.loop.run_in_executor, None, self._run
        )

    def _run(self):
        try:
            self._func(self._bot)
        except:
            traceback.print_exc()
        self._set()

    def stop(self):
        self._handler.cancel()
