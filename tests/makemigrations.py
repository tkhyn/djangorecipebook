import os
import shutil

from ._base import mock, ScriptTests, RecipeTests

from djangorecipebook.scripts.makemigrations import main
from djangorecipebook.recipes.makemigrations import Recipe
from djangorecipebook.exceptions import ImproperlyConfigured


@mock.patch('sys.stdout', open(os.devnull, 'w'))
class MigrationScriptTests(ScriptTests):

    maxDiff = None

    def setUp(self):
        super(MigrationScriptTests, self).setUp()
        from django.conf import settings, empty
        settings._wrapped = empty

    @mock.patch('sys.argv', ['makemigrations', 'app3'])
    @mock.patch('django.conf.LazySettings.configure')
    @mock.patch('django.core.management.execute_from_command_line')
    def test_main(self, mock_execute, mock_configure):
        # The manage script is a replacement for the default manage.py
        # script. It has all the same bells and whistles since all it
        # does is call the normal Django stuff.
        apps = ('app1', 'app2')

        main({}, *apps)

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
