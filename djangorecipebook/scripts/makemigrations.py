"""
Calls the management script with the 'makemigrations' command
Also runs south's 'schemamigration' if applicable
"""

import sys
from copy import copy

import django

from .manage import manage_main


def main(settings, *args, **kwargs):

    # detect --init flag and removes it from args to run makemigrations
    try:
        south_init = sys.argv.pop(sys.argv.index('--init'))
    except ValueError:
        # --init not found
        south_init = False

    if django.VERSION >= (1, 7):
        # run django migrations if django >= 1.7

        # we backyp sys.argv as we'll need to restore it if schemamigration
        # should be ran afterwards, as manage_main amends sys.argv
        argv = copy(sys.argv)

        manage_main(settings, 'makemigrations', *args)

        # restore sys.argv
        sys.argv = argv

    if kwargs.pop('use_south', False) or django.VERSION < (1, 7):

        # south is not required here, but trying to import it will raise an
        # ImportError if it is not available
        import south

        if isinstance(settings, dict):
            # adds south to INSTALLED_APPS if we're using minimal settings
            settings['INSTALLED_APPS'] = settings.get('INSTALLED_APPS', ()) \
                                         + ('south',)

        # use --auto flag if --init flag was not provided
        sys.argv.append(south_init or '--auto')

        # run south migrations
        manage_main(settings, 'schemamigration', *args)
