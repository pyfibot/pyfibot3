import os
from fnmatch import fnmatch
from pyfibot.decorators import admin_command


ENABLED_PLUGINS_DIR = os.path.abspath(os.path.dirname(__file__))


def get_python_scripts(directory):
    return {
        filename.replace('.py', ''): os.path.join(directory, filename)
        for filename in os.listdir(directory) if fnmatch(filename, '*.py') and filename != '__init__.py'
    }


def get_enabled_plugins():
    return get_python_scripts(ENABLED_PLUGINS_DIR)


def get_available_plugins():
    return get_python_scripts(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'available'))


@admin_command('list_available_plugins')
def list_available_plugins(bot, sender, message, message_arguments):
    ''' List all available bot plugins. Only for admins. '''

    enabled_plugins = get_enabled_plugins().keys()
    available_plugins = sorted([
        plugin
        for plugin in get_available_plugins().keys() if plugin not in enabled_plugins
    ])
    bot.respond('Available plugins: %s' % (', '.join(available_plugins)), message_arguments)


@admin_command('enable_plugin')
def enable_plugin(bot, sender, message, message_arguments):
    ''' Enable an available bot plugin. Only for admins. '''

    available_plugins = get_available_plugins()
    if message not in available_plugins.keys():
        return bot.respond('Plugin "%s" does not exist.' % message, message_arguments)

    if message in get_enabled_plugins().keys():
        return bot.respond('Plugin "%s" is already enabled.' % message, message_arguments)

    os.symlink(available_plugins[message], os.path.join(ENABLED_PLUGINS_DIR, '%s.py' % message))

    bot.load_plugins()
    bot.respond('plugin "%s" enabled.' % message, message_arguments)


@admin_command('disable_plugin')
def disable_plugin(bot, sender, message, message_arguments):
    ''' Disable a bot plugin. Only for admins. '''

    enabled_plugins = get_enabled_plugins()
    if message not in enabled_plugins.keys():
        return bot.respond('Plugin "%s" isn\'t enabled.' % message, message_arguments)

    if not os.path.islink(enabled_plugins[message]):
        return bot.respond('Plugin "%s" is a core plugin and cannot be disabled.' % message, message_arguments)

    os.unlink(enabled_plugins[message])

    bot.load_plugins()
    bot.respond('Plugin "%s" disabled.' % message, message_arguments)
