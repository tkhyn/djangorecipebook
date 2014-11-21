import os
import mock

from ._base import ScriptTests, RecipeTests

from djangorecipebook.scripts.manage import main
from djangorecipebook.recipes.manage import Recipe


class ManageScriptTests(ScriptTests):

    @mock.patch('sys.argv', ['manage'])
    @mock.patch('django.core.management.execute_from_command_line')
    def test_script_settings_module(self, mock_execute):
        # The manage script is a replacement for the default manage.py
        # script. It has all the same bells and whistles since all it
        # does is call the normal Django stuff.
        main('settings_module')
        self.assertListEqual(mock_execute.call_args[0][0],
                             ['manage.py', '--settings=settings_module'])


    @mock.patch('sys.argv', ['manage'])
    @mock.patch('django.conf.LazySettings.configure')
    @mock.patch('django.core.management.execute_from_command_line')
    def test_script_settings_dict(self, mock_execute, mock_configure):
        # check that the added settings (as a dictionnary) are correctly
        # transmitted to settings.configure
        main({'INSTALLED_APPS': ('app1', 'app2')})
        self.assertListEqual(mock_execute.call_args[0][0], ['manage.py'])
        self.assertTupleEqual(mock_configure.call_args[1]['INSTALLED_APPS'], (
                                  'django.contrib.admin',
                                  'django.contrib.auth',
                                  'django.contrib.contenttypes',
                                  'django.contrib.sessions',
                                  'django.contrib.messages',
                                  'django.contrib.staticfiles',
                                  'app1',
                                  'app2'))



class ManageRecipeTests(RecipeTests):

    recipe_class = Recipe
    recipe_name = 'manage'
    recipe_options = {'recipe': 'djangorecipebook:manage'}

    def test_consistent_options(self):
        options_1 = self.recipe.options
        self.init_recipe()
        self.assertEqual(options_1, self.recipe.options)

    @mock.patch('zc.recipe.egg.egg.Scripts.working_set',
                return_value=(None, []))
    def test_install(self, working_set):
        # Default install of a management script, check that the call to
        # djangorecipebook.manage.main is present
        self.recipe.install()
        manage_script = self.script_path('manage')
        self.assertTrue(os.path.exists(manage_script))
        self.assertIn("djangorecipebook.scripts.manage.main(added_settings)",
                      self.script_cat(manage_script))
