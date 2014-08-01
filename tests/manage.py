import os
import sys
import mock

from .base import ScriptTests, RecipeTests, test_settings

from djangorecipebook.scripts.manage import main
from djangorecipebook.recipes.manage import Recipe


class ManageScriptTests(ScriptTests):

    @mock.patch('django.core.management.execute_from_command_line')
    def test_script(self, mock_execute):
        # The manage script is a replacement for the default manage.py
        # script. It has all the same bells and whistles since all it
        # does is call the normal Django stuff.
        main(test_settings)
        self.assertListEqual(mock_execute.call_args[0][0],
                             sys.argv + ['--settings=%s' % test_settings])


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
        self.assertIn("djangorecipebook.scripts.manage.main('%s')" % \
                        test_settings,
                      self.script_cat(manage_script))
