import os
# import time
# import random
import dataset


class Database(object):
    '''
    Connector to the bot's database. To be used via with-statement:

        with Database(bot) as db:
            # do something with database.
            table = db['test']
            test.insert({'message': 'test message'})

    Provides a dataset-interface to the SQLite3 database.
    See: https://dataset.readthedocs.io/en/latest/

    '''

    def __init__(self, bot):
        self._core = bot.core
        self._database_file = os.path.join(self._core.configuration_path, 'database.sqlite3')
        self._database_lock_file = os.path.join(self._core.configuration_path, 'database.lock')

        self._database_instance = None

    def __enter__(self, *args, **kwargs):
        # Wait for lockfile to release
        while os.path.exists(self._database_lock_file):
            pass
            # # Sleep for random time between 1 and 10 milliseconds
            # time.sleep(random.randrange(1, 10) / 1000)

        # Create lockfile
        with open(self._database_lock_file, 'w'):
            pass

        # Initialize database instance
        self._database_instance = dataset.connect('sqlite:///%s' % self._database_file)
        return self._database_instance

    def __exit__(self, *args, **kwargs):
        os.unlink(self._database_lock_file)
