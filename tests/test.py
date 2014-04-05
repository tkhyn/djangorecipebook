import os
import sys
import mock

from base import ScriptTests, RecipeTests, test_settings

from djangorecipebook.recipes import test


class TestScriptTests(ScriptTests):

    @mock.patch('django.core.management.execute_from_command_line')
    @mock.patch('os.environ.setdefault')
    def test_script(self, mock_setdefault, mock_execute):
        # The manage script is a replacement for the default manage.py
        # script. It has all the same bells and whistles since all it
        # does is call the normal Django stuff.
        apps = ('app1', 'app2')
        test.main(test_settings, *apps)
        self.assertListEqual(mock_execute.call_args[0][0],
                             ['test', 'test'] + list(apps))
        self.assertTupleEqual(mock_setdefault.call_args,
                              (('DJANGO_SETTINGS_MODULE', test_settings), {}))


class TestRecipeTests(RecipeTests):

    recipe_class = test.Recipe
    recipe_name = 'test'
    recipe_options = {'recipe': 'djangorecipebook:test'}

    @mock.patch('zc.recipe.egg.egg.Scripts.working_set',
                return_value=(None, []))
    def test_install_all_apps(self, working_set):
        # Default install of a test script, check that the call to
        # djangorecipebook.test.main is present and has no other arguments
        # than the settings and 'test'
        self.recipe.install()
        test_script = self.script_path('test')
        self.assertTrue(os.path.exists(test_script))
        self.assertIn(("djangorecipebook.recipes.test.main('%s')" % \
                     test_settings), self.script_cat(test_script))

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
        self.assertIn("djangorecipebook.recipes.test.main('%s', %s)" % \
                        (test_settings,
                         ', '.join(["'%s'" % app for app in apps])),
                      self.script_cat(test_script))
