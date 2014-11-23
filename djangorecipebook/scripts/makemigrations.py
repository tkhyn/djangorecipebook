"""
Calls the management script with the 'makemigrations' command
Also runs south's 'schemamigration' if applicable
"""

import os
import sys
from subprocess import Popen
from importlib import import_module
import imp
import shutil

from .manage import manage_main


class SouthWarning(Warning):
    pass


def make_django_migrations(settings, args):
    # remove any south-specific flag from args
    for arg in reversed(args):
        if arg in ('--initial', '--auto', '--update'):
            args.remove(arg)
    manage_main(settings, 'makemigrations', *args)


def make_south_migrations(settings, args, south_dir=False):
    # remove any django-specific flag from args
    for arg in reversed(args):
        if arg in ('--dry-run', '--merge', '--name'):
            args.remove(arg)

    # automatic auto mode?
    south_flags = set(['--auto', '--initial', '--add-field', '--empty'])
    auto_auto = south_flags.isdisjoint(args)
    if auto_auto:
        # default mode is 'auto'
        args.append('--auto')

    if not isinstance(settings, dict):
        # converting settings to a dictionary, so that we can add south in
        # INSTALLED_APPS if needed (indeed, when this script is called from
        # a django 1.7 installation, south is not in INSTALLED_APPS)
        # there should be no problems while importing a settings module, as
        # it should not depend on django's internals
        settings = import_module(settings).__dict__

    if 'south' not in settings.get('INSTALLED_APPS', ()):
        settings['INSTALLED_APPS'] = settings.get('INSTALLED_APPS', ()) \
                                     + ('south',)

    south_mig_modules = settings.setdefault('SOUTH_MIGRATION_MODULES', {})

    inst_apps = settings['INSTALLED_APPS']
    apps_to_migrate = set(inst_apps).intersection(args)
    apps_to_init = set(apps_to_migrate if '--initial' in args else [])

    # if in 'automatic auto' mode, gather the apps that need to be initialized
    if auto_auto or south_dir:
        for app in list(apps_to_migrate):
            # 1. find the app location path
            app_py_path = app.split('.')
            app_py_path.reverse()
            path = imp.find_module(app_py_path.pop())[1]
            while app_py_path:
                path = os.path.join(path, app_py_path.pop())

            # 2. check if the 'migration' or 'south_migration' subpackages
            # contain south migrations

            south_mig_pkg = None

            for subpkg in ('migrations', 'south_migrations'):
                mig_path = os.path.join(path, subpkg)

                if os.path.isfile(os.path.join(mig_path, '__init__.py')):
                    # there is a migration subpackage, look for the first
                    # migration file
                    for f in os.listdir(mig_path):
                        if f.endswith('.py') and f != '__init__.py':
                            # migration found, check if it is a south migration
                            mig = open(os.path.join(mig_path, f))
                            found_mig = 'from south.db import db' in mig.read()
                            mig.close()
                            break
                    else:
                        found_mig = False

                    if found_mig:
                        south_mig_pkg = subpkg
                        break

            if south_mig_pkg is None:
                # no south migration package found
                if auto_auto:
                    apps_to_init.add(app)
                    apps_to_migrate.discard(app)
                if south_dir:
                    south_mig_modules[app] = app + '.south_migrations'
            else:
                apps_to_init.discard(app)
                apps_to_migrate.add(app)
                if south_mig_pkg == 'migrations' and south_dir:
                    # if we want the south migrations to be in
                    # their own south_migrations directory, move them
                    south_mig_path = os.path.join(path, 'south_migrations')
                    if os.path.isdir(south_mig_path):
                        shutil.rmtree(south_mig_path)
                    os.rename(mig_path, south_mig_path)

    if apps_to_init:
        init_args = []
        for a in args:
            if not a in south_flags \
            and (a.startswith('-') or not a in inst_apps or a in apps_to_init):
                init_args.append(a)
        manage_main(settings, 'schemamigration', '--init', *init_args)

    if apps_to_migrate:
        migrate_args = []
        for a in args:
            if a.startswith('-') or not a in inst_apps or a in apps_to_migrate:
                migrate_args.append(a)
        manage_main(None if apps_to_init else settings, 'schemamigration',
                    *migrate_args)


def make_south_from_dj17(settings, *args):
    try:
        import south
    except ImportError:
        raise SouthWarning('Could not import south. '
                           'Skipping south migrations generation')

    sys_argv = sys.argv[1:]
    sys.argv = sys.argv[:1]

    make_south_migrations(settings, list(args) + sys_argv,
                          south_dir=True)


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
        except ImportError:
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

            sys.stderr.write('\nGenerating south migrations\n'
                             '---------------------------\n\n')

            Popen([dj16script] + sys_argv).wait()

            sys.stderr.write('\nGenerating django migrations\n'
                             '----------------------------\n\n')

        make_django_migrations(settings, args + sys_argv)
