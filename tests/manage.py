import os
import sys
import mock

from base import ScriptTests, RecipeTests, test_settings

from djangorecipebook.recipes import manage


class ManageScriptTests(ScriptTests):

    @mock.patch('django.core.management.execute_from_command_line')
    @mock.patch('os.environ.setdefault')
    def test_script(self, mock_setdefault, mock_execute):
        # The manage script is a replacement for the default manage.py
        # script. It has all the same bells and whistles since all it
        # does is call the normal Django stuff.
        manage.main(test_settings)
        self.assertTupleEqual(mock_execute.call_args,
                              ((sys.argv,), {}))
        self.assertTupleEqual(mock_setdefault.call_args,
                              (('DJANGO_SETTINGS_MODULE', test_settings), {}))


class ManageRecipeTests(RecipeTests):

    recipe_class = manage.Recipe
    recipe_name = 'manage'
    recipe_options = {'recipe': 'djangorecipebook:manage'}

    @mock.patch('zc.recipe.egg.egg.Scripts.working_set',
                return_value=(None, []))
    def test_install(self, working_set):
        # Default install of a management script, check that the call to
        # djangorecipebook.manage.main is present
        self.recipe.install()
        manage_script = self.script_path('manage')
        self.assertTrue(os.path.exists(manage_script))
        self.assertIn(("djangorecipebook.recipes.manage.main('%s')" % \
                     test_settings), self.script_cat(manage_script))
