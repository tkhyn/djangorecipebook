"""
Recipe generating a management script
"""

import sys


def manage_main(settings_module, command, *args):
    from django.core import management
    settings = []
    for arg in sys.argv:
        if arg.startswith('--settings='):
            break
    else:
        settings = ['--settings=%s' % settings_module]

    if command:
        command = [command]
    else:
        command = []

    # the arguments need to be inserted in sys.argv as subsequent packages
    # (e.g. nose) may use sys.argv and forget about what is passed to manage.py
    sys.argv[1:1] = args
    management.execute_from_command_line(['manage.py'] + command +
                                         settings + sys.argv[1:])


def main(settings_module, *args):
    manage_main(settings_module, None, *args)
