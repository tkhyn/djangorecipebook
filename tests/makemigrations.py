import os
import sys
import shutil

try:
    # python 3
    import builtins
except ImportError:
    # python 2
    import __builtin__ as builtins

import django
from django.utils.six import iteritems

from ._base import mock, ScriptTests, RecipeTests

from djangorecipebook.scripts.makemigrations \
    import main, make_south_migrations, make_south_from_dj17, SouthWarning
from djangorecipebook.recipes.makemigrations import Recipe
from djangorecipebook.exceptions import ImproperlyConfigured


@mock.patch('sys.stdout', open(os.devnull, 'w'))
class MigrationScriptTests(ScriptTests):

    maxDiff = None

    @mock.patch('sys.argv', ['makemigrations', 'app3'])
    @mock.patch('djangorecipebook.scripts.makemigrations.Popen')
    @mock.patch('django.conf.LazySettings.configure')
    @mock.patch('django.core.management.execute_from_command_line')
    def test_main(self, mock_execute, mock_configure, mock_popen):
        # The manage script is a replacement for the default manage.py
        # script. It has all the same bells and whistles since all it
        # does is call the normal Django stuff.
        apps = ('app1', 'app2')

        # mocks existence of south module
        south_installed = 'south' in sys.modules
        if not south_installed:
            sys.modules['south'] = mock.Mock()

        main({}, *apps, dj16script='dj16south_script')

        if not south_installed:
            sys.modules.pop('south')

        if django.VERSION >= (1, 7):
            # check that Popen has been called with the script address
            # this is supposed to call south's schemamigration command
            self.assertListEqual(mock_popen.call_args[0][0],
                                 ['dj16south_script', 'app3'])

            # calling django's makemigrations
            self.assertListEqual(mock_execute.call_args[0][0],
                                 ['manage.py', 'makemigrations',
                                  'app1', 'app2', 'app3'])
            self.assertTupleEqual(
                mock_configure.call_args[1]['INSTALLED_APPS'],
                ('django.contrib.admin',
                 'django.contrib.auth',
                 'django.contrib.contenttypes',
                 'django.contrib.sessions',
                 'django.contrib.messages',
                 'django.contrib.staticfiles'))
        else:
            # calling only south's schemamigration
            self.assertListEqual(mock_execute.call_args[0][0],
                                 ['manage.py', 'schemamigration',
                                  'app1', 'app2', 'app3', '--auto'])
            self.assertTupleEqual(
                mock_configure.call_args[1]['INSTALLED_APPS'],
                ('django.contrib.admin',
                 'django.contrib.auth',
                 'django.contrib.contenttypes',
                 'django.contrib.sessions',
                 'django.contrib.messages',
                 'django.contrib.staticfiles',
                 'south'))

    @mock.patch('sys.argv', ['makemigrations', '--initial'])
    @mock.patch('djangorecipebook.scripts.makemigrations.Popen')
    @mock.patch('django.conf.LazySettings.configure')
    @mock.patch('django.core.management.execute_from_command_line')
    def test_main_initial(self, mock_execute, mock_configure, mock_popen):
        # with --initial flag

        # mocks existence of south module
        south_installed = 'south' in sys.modules
        if not south_installed:
            sys.modules['south'] = mock.Mock()

        main({}, dj16script='dj16south_script')

        if not south_installed:
            sys.modules.pop('south')

        if django.VERSION >= (1, 7):
            # calling dj16 script with --initial
            self.assertListEqual(mock_popen.call_args[0][0],
                                 ['dj16south_script', '--initial'])
            # calling makemigrations, no '--initial' arg
            self.assertListEqual(mock_execute.call_args[0][0],
                                 ['manage.py', 'makemigrations'])
        else:
            # calling south's schemamigration with --initial arg
            self.assertListEqual(mock_execute.call_args[0][0],
                                 ['manage.py', 'schemamigration', '--initial'])


    @mock.patch('sys.argv', ['makemigrations'])
    @mock.patch('djangorecipebook.scripts.makemigrations.Popen')
    @mock.patch('django.core.management.execute_from_command_line')
    def test_script_south_unavailable(self, mock_execute, mock_popen):

        # monkeypatching __import__ to raise ImportError when importing south
        import0 = builtins.__import__

        def myimport(name, *args, **kwargs):
            if name == 'south':
                raise ImportError
            return import0(name, *args, **kwargs)
        builtins.__import__ = myimport

        with self.assertRaises((ImportError, SouthWarning)):
            make_south_from_dj17('settings')

        builtins.__import__ = import0


    @mock.patch('sys.argv', ['makemigrations'])
    @mock.patch('os.rename')
    @mock.patch('django.conf.LazySettings.configure')
    @mock.patch('django.core.management.execute_from_command_line')
    def test_make_south(self, mock_execute, mock_configure, mock_rename):

        make_south_migrations('tests.mig_project.settings', [], south_dir=True)

        projpath = os.path.join(os.path.dirname(__file__),
                                    'mig_project')

        self.assertTupleEqual(mock_rename.call_args[0],
            (os.path.join(projpath, 'migrated_with_south', 'migrations'),
             os.path.join(projpath, 'migrated_with_south', 'south_migrations'))
        )

        from tests.mig_project import settings
        settings_dict = dict([(k, v) for k, v in iteritems(settings.__dict__)
                              if k.isupper()])

        settings_dict['INSTALLED_APPS'] += ('south',)
        settings_dict['SOUTH_MIGRATION_MODULES'] = {
            'tests.mig_project.migrated_with_dj17':
                'tests.mig_project.migrated_with_dj17.south_migrations',
            'tests.mig_project.unmigrated':
                'tests.mig_project.unmigrated.south_migrations',
        }

        self.assertDictEqual(mock_configure.call_args[1], settings_dict)

        self.assertListEqual(mock_execute.call_args_list[0][0][0][:3],
                             ['manage.py', 'schemamigration', '--initial'])
        self.assertSetEqual(set(mock_execute.call_args_list[0][0][0][3:]),
                            set(['tests.mig_project.migrated_with_dj17',
                                 'tests.mig_project.unmigrated']))

        self.assertListEqual(mock_execute.call_args_list[1][0][0][:3],
                             ['manage.py', 'schemamigration', '--auto'])
        self.assertSetEqual(set(mock_execute.call_args_list[1][0][0][3:]),
                            set(['tests.mig_project.migrated_with_both',
                                 'tests.mig_project.migrated_with_south']))


class MakeMigrationsRecipeTests(RecipeTests):

    recipe_class = Recipe
    recipe_name = 'makemigrations'
    recipe_options = {'recipe': 'djangorecipebook:makemigrations'}

    def tearDown(self):
        parts_dir = self.recipe.buildout['buildout']['parts-directory']
        if os.path.isdir(parts_dir):
            shutil.rmtree(parts_dir)

    def test_consistent_options(self):
        options_1 = self.recipe.options
        self.init_recipe()
        self.assertEqual(options_1, self.recipe.options)

    @mock.patch('zc.recipe.egg.egg.Scripts.working_set',
                return_value=(None, []))
    def test_install_no_apps_no_settings(self, working_set):
        # This should raise an exception as no settings module nor app is
        # provided
        with self.assertRaises(ImproperlyConfigured):
            self.recipe.install()

    @mock.patch('zc.recipe.egg.egg.Scripts.working_set',
                return_value=(None, []))
    def test_install_with_settings(self, working_set):
        # A settings file is provided, we can therefore expect it defines apps
        # to generate migrations for
        self.init_recipe({'settings': 'settings'})
        self.recipe.install()  # no error
        migrations_script = self.script_path('makemigrations')
        self.assertTrue(os.path.exists(migrations_script))
        self.assertIn(
            "djangorecipebook.scripts.makemigrations.main('settings')",
            self.script_cat(migrations_script))

    @mock.patch('zc.recipe.egg.egg.Scripts.working_set',
                return_value=(None, []))
    def test_install_with_apps(self, working_set):
        # Apps - but no settings file - are provided, a minimal settings file
        # is generated in the parts directory
        inst_apps = ('app1', 'app2')
        apps = ('app3',)
        self.init_recipe({'inst_apps': '\n    '.join(inst_apps),
                          'apps': '\n    '.join(apps)})
        self.recipe.install()
        migrations_script = self.script_path('makemigrations')
        script_cat = self.script_cat(migrations_script)
        self.assertIn("djangorecipebook.scripts.makemigrations"
                      ".main(added_settings, 'app3')", script_cat)
        self.assertIn("{'INSTALLED_APPS': ('app1', 'app2', 'app3')}",
                      script_cat)

    @mock.patch('zc.recipe.egg.egg.Scripts.working_set',
                return_value=(None, []))
    def test_packages_with_dj17_and_south(self, working_set):
        # south is set
        self.init_recipe({'settings': 'settings',
                          'south': '1'})

        self.recipe.install()

        migrations_script = self.script_path('makemigrations')
