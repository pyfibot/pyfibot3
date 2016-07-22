import os
from fnmatch import fnmatch
from pyfibot.decorators import admin_command


ENABLED_MODULES_DIR = os.path.abspath(os.path.dirname(__file__))


def get_python_scripts(directory):
    return {
        filename.replace('.py', ''): os.path.join(directory, filename)
        for filename in os.listdir(directory) if fnmatch(filename, '*.py') and filename != '__init__.py'
    }


def get_enabled_modules():
    return get_python_scripts(ENABLED_MODULES_DIR)


def get_available_modules():
    return get_python_scripts(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'available'))


@admin_command('list_available_modules')
def list_available_modules(bot, sender, message, message_arguments):
    ''' List all available bot modules. Only for admins. '''

    enabled_modules = get_enabled_modules().keys()
    available_modules = sorted([
        module
        for module in get_available_modules().keys() if module not in enabled_modules
    ])
    bot.respond('Available modules: %s' % (', '.join(available_modules)), message_arguments)


@admin_command('enable_module')
def enable_module(bot, sender, message, message_arguments):
    ''' Enable an available bot module. Only for admins. '''

    available_modules = get_available_modules()
    if message not in available_modules.keys():
        return bot.respond('Module "%s" does not exist.' % message, message_arguments)

    if message in get_enabled_modules().keys():
        return bot.respond('Module "%s" is already enabled.' % message, message_arguments)

    os.symlink(available_modules[message], os.path.join(ENABLED_MODULES_DIR, '%s.py' % message))

    bot.load_plugins()
    bot.respond('Module "%s" enabled.' % message, message_arguments)


@admin_command('disable_module')
def disable_module(bot, sender, message, message_arguments):
    ''' Disable a bot module. Only for admins. '''

    enabled_modules = get_enabled_modules()
    if message not in enabled_modules.keys():
        return bot.respond('Module "%s" isn\'t enabled.' % message, message_arguments)

    if not os.path.islink(enabled_modules[message]):
        return bot.respond('Module "%s" is a core module and cannot be disabled.' % message, message_arguments)

    os.unlink(enabled_modules[message])

    bot.load_plugins()
    bot.respond('Module "%s" disabled.' % message, message_arguments)
