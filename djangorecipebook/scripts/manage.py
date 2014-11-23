"""
Calls django's management script
"""

import sys


DEFAULT_SETTINGS = dict(
    SECRET_KEY='secret',
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3'
        }
    },
    MIDDLEWARE_CLASSES=(),
    INSTALLED_APPS=(
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
    )
)


def manage_main(settings, command, *args):

    settings_arg = []
    for arg in sys.argv:
        if arg.startswith('--settings='):
            break
    else:
        from django.conf import settings as dj_settings
        from django.utils.six import string_types

        if isinstance(settings, string_types):
            settings_arg = ['--settings=' + settings]
        else:
            # using default settings, eventually amended
            if isinstance(settings, dict):
                new_settings = dict(DEFAULT_SETTINGS)  # make a copy
                new_settings['INSTALLED_APPS'] += \
                    settings.pop('INSTALLED_APPS', ())
                new_settings.update(settings)
            else:
                new_settings = DEFAULT_SETTINGS
            dj_settings.configure(**new_settings)

    if command:
        command = [command]
    else:
        try:
            command = [sys.argv.pop(1)]
        except IndexError:
            raise ValueError('No django command found. A django command is '
                             'required when calling manage.py.')

    # the arguments need to be inserted in sys.argv as subsequent packages
    # (e.g. nose) may use sys.argv and forget about what is passed to manage.py
    sys.argv[1:1] = args

    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py'] + command +
                              settings_arg + sys.argv[1:])


def main(settings, *args):
    manage_main(settings, None, *args)
