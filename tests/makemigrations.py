import os
import sys

try:
    # python 3
    import builtins
except ImportError:
    # python 2
    import __builtin__ as builtins

import mock

import django
from django.core.exceptions import ImproperlyConfigured

from ._base import ScriptTests, RecipeTests

from djangorecipebook.scripts.makemigrations import main
from djangorecipebook.recipes.makemigrations import Recipe


class MigrationScriptTests(ScriptTests):

    @mock.patch('sys.argv', ['makemigrations'])
    @mock.patch('django.conf.LazySettings.configure')
    @mock.patch('django.core.management.execute_from_command_line')
    def test_script(self, mock_execute, mock_configure):
        # The manage script is a replacement for the default manage.py
        # script. It has all the same bells and whistles since all it
        # does is call the normal Django stuff.
        apps = ('app1', 'app2')

        # mocks existence of south module
        south_installed = 'south' in sys.modules
        if not south_installed:
            sys.modules['south'] = mock.Mock()

        main({}, *apps, use_south=True)

        if not south_installed:
            sys.modules.pop('south')

        if django.VERSION >= (1, 7):
            # calling makemigrations
            self.assertListEqual(mock_execute.call_args_list[0][0][0],
                                 ['manage.py', 'makemigrations',
                                  'app1', 'app2'])
            self.assertTupleEqual(
                mock_configure.call_args_list[0][1]['INSTALLED_APPS'],
                ('django.contrib.admin',
                 'django.contrib.auth',
                 'django.contrib.contenttypes',
                 'django.contrib.sessions',
                 'django.contrib.messages',
                 'django.contrib.staticfiles'))

        # calling south's schemamigration
        self.assertListEqual(mock_execute.call_args_list[-1][0][0],
                             ['manage.py', 'schemamigration', 'app1', 'app2',
                              '--auto'])
        self.assertTupleEqual(
            mock_configure.call_args_list[-1][1]['INSTALLED_APPS'],
            ('django.contrib.admin',
             'django.contrib.auth',
             'django.contrib.contenttypes',
             'django.contrib.sessions',
             'django.contrib.messages',
             'django.contrib.staticfiles',
             'south'))

    @mock.patch('sys.argv', ['makemigrations', '--init'])
    @mock.patch('django.conf.LazySettings.configure')
    @mock.patch('django.core.management.execute_from_command_line')
    def test_script_init(self, mock_execute, mock_configure):
        # with --init flag

        # mocks existence of south module
        south_installed = 'south' in sys.modules
        if not south_installed:
            sys.modules['south'] = mock.Mock()

        main({}, use_south=True)

        if not south_installed:
            sys.modules.pop('south')

        if django.VERSION >= (1, 7):
            # calling makemigrations, no '--init' arg
            self.assertListEqual(mock_execute.call_args_list[0][0][0],
                                 ['manage.py', 'makemigrations'])

        # calling south's schemamigration with --init arg
        self.assertListEqual(mock_execute.call_args_list[-1][0][0],
                             ['manage.py', 'schemamigration', '--init'])



    @mock.patch('sys.argv', ['makemigrations'])
    @mock.patch('django.core.management.execute_from_command_line')
    def test_script_south_unavailable(self, mock_execute):

        # monkeypatching __import__ to raise ImportError when importing south
        import0 = builtins.__import__

        def myimport(name, *args, **kwargs):
            if name == 'south':
                raise ImportError
            return import0(name, *args, **kwargs)
        builtins.__import__ = myimport

        with self.assertRaises(ImportError):
            main('settings', use_south=True)

        builtins.__import__ = import0



class MakeMigrationsRecipeTests(RecipeTests):

    recipe_class = Recipe
    recipe_name = 'makemigrations'
    recipe_options = {'recipe': 'djangorecipebook:makemigrations'}

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
    def test_install_with_south(self, working_set):
        # Apps - but no settings file - are provided, a minimal settings file
        # is generated in the parts directory
        self.init_recipe({'settings': 'settings'})
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
