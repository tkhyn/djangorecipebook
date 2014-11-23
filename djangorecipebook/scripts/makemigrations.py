"""
Calls the management script with the 'makemigrations' command
Also runs south's 'schemamigration' if applicable
"""

import sys
from subprocess import Popen
from importlib import import_module

from .manage import manage_main


class SouthWarning(Warning):
    pass


def make_django_migrations(settings, args):
    # remove any south-specific flag from args
    for arg in reversed(args):
        if arg in ('--initial', '--auto', '--update'):
            args.remove(arg)
    manage_main(settings, 'makemigrations', *args)


def make_south_migrations(settings, args):
    # remove any django-specific flag from args
    for arg in reversed(args):
        if arg in ('--dry-run', '--merge', '--name'):
            args.remove(arg)
    if set(['--auto', '--initial', '--add-field', '--empty']).isdisjoint(args):
        # default mode is 'auto'
        args.append('--auto')

    if not isinstance(settings, dict):
        # converting settings to a dictionary, so that we can add south in
        # INSTALLED_APPS if needed (indeed, when this script is called from
        # a django 1.7 installation, south is not in INSTALLED_APPS)
        settings = import_module(settings).__dict__

    if 'south' not in settings.get('INSTALLED_APPS', ()):
        settings['INSTALLED_APPS'] = settings.get('INSTALLED_APPS', ()) \
                                     + ('south',)

    manage_main(settings, 'schemamigration', *args)


def main(settings, *args, **kwargs):

    # we empty sys.argv so that command line params can be intercepted
    # by the make_*_migrations functions above
    sys_argv = sys.argv[1:]
    sys.argv = sys.argv[:1]

    args = list(args)

    import django
    if django.VERSION < (1, 7):
        # for django < 1.7, we only generate south migrations

        # south itself is not required here, but trying to import it will raise
        # an ImportError if it is not available
        try:
            import south
        except ImportError as e:
            raise ImportError(
                'Could not import south and running Django < 1.7. '
                'No migrations could be generated.'
            )

        make_south_migrations(settings, args + sys_argv)

    else:
        # for django >= 1.7, we generate django migrations, and possibly
        # south migrations as well by launching a secondary script in a
        # separate process

        dj16script = kwargs.pop('dj16script', False)
        if dj16script:
            # launch secondary dj16/south script with command line args

            # south itself is not required here, but trying to import it will
            # raise a warning
            try:
                import south
            except ImportError as e:
                raise SouthWarning('Could not import south. '
                                   'Skipping south migrations generation')

            sys.stderr.write('\nGenerating south migrations\n'
                             '---------------------------\n\n')

            Popen([dj16script] + sys_argv).wait()

            sys.stderr.write('\nGenerating django migrations\n'
                             '----------------------------\n\n')

        make_django_migrations(settings, args + sys_argv)
