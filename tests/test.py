import os
import sys
import mock

from .base import ScriptTests, RecipeTests, test_settings

from djangorecipebook.scripts.test import main
from djangorecipebook.recipes.test import Recipe


class TestScriptTests(ScriptTests):

    @mock.patch('sys.argv', ['test'])
    @mock.patch('django.core.management.execute_from_command_line')
    def test_script(self, mock_execute):
        # The manage script is a replacement for the default manage.py
        # script. It has all the same bells and whistles since all it
        # does is call the normal Django stuff.
        apps = ('app1', 'app2')
        main(test_settings, *apps)
        self.assertListEqual(mock_execute.call_args[0][0],
                             ['manage.py', 'test'] + sys.argv[1:] + \
                             ['--settings=%s' % test_settings] + list(apps))


class TestRecipeTests(RecipeTests):

    recipe_class = Recipe
    recipe_name = 'test'
    recipe_options = {'recipe': 'djangorecipebook:test'}

    def test_consistent_options(self):
        options_1 = self.recipe.options
        self.init_recipe()
        self.assertEqual(options_1, self.recipe.options)

    @mock.patch('zc.recipe.egg.egg.Scripts.working_set',
                return_value=(None, []))
    def test_install_all_apps(self, working_set):
        # Default install of a test script, check that the call to
        # djangorecipebook.test.main is present and has no other arguments
        # than the settings and 'test'
        self.recipe.install()
        test_script = self.script_path('test')
        self.assertTrue(os.path.exists(test_script))
        self.assertIn("djangorecipebook.scripts.test.main('%s')" % \
                        test_settings,
                      self.script_cat(test_script))

    @mock.patch('zc.recipe.egg.egg.Scripts.working_set',
                return_value=(None, []))
    def test_install_with_apps(self, working_set):
        # Default install of a test script, check that the call to
        # djangorecipebook.test.main is present and has the apps names in the
        # arguments
        apps = ('app1', 'app2')
        self.init_recipe({'apps': '\n    '.join(apps)})
        self.recipe.install()
        test_script = self.script_path('test')
        self.assertIn("djangorecipebook.scripts.test.main('%s', %s)" % \
                        (test_settings,
                         ', '.join(["'%s'" % app for app in apps])),
                      self.script_cat(test_script))

    @mock.patch('zc.recipe.egg.egg.Scripts.working_set',
                return_value=(None, []))
    def test_install_with_nose(self, working_set):
        # Install of a test script with nose
        self.init_recipe({'nose': '1'})
        self.recipe.install()
        self.assertListEqual(working_set.call_args[0][0],
                             ['djangorecipebook', 'djangorecipebook[nose]'])

    @mock.patch('zc.recipe.egg.egg.Scripts.working_set',
                return_value=(None, []))
    def test_install_workingdir(self, working_set):
        # Install of a test script with a working directory
        self.init_recipe({'workingdir': 'tests'})
        self.recipe.install()
        test_script = self.script_path('test')
        self.assertIn("import os\n"
                      "os.chdir('tests')\n"
                      "sys.path.append(os.getcwd())",
                      self.script_cat(test_script))
