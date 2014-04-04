import os
import sys
import mock

from base import ScriptTests, RecipeTests, test_project, test_settings

from djangorecipebook.recipes import manage


class ManageScriptTests(ScriptTests):

    @mock.patch('django.core.management.execute_from_command_line')
    @mock.patch('os.environ.setdefault')
    def test_script(self, mock_setdefault, mock_execute):
        # The manage script is a replacement for the default manage.py
        # script. It has all the same bells and whistles since all it
        # does is call the normal Django stuff.
        manage.main(test_settings)
        self.assertEqual(mock_execute.call_args,
                         ((sys.argv,), {}))
        self.assertEqual(
            mock_setdefault.call_args,
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

    @mock.patch('zc.recipe.egg.egg.Scripts.working_set',
                return_value=(None, []))
    def test_create_manage_script_projectdir(self, working_set):
        # When a project dir is specified, it should be added to sys.path
        self.init_recipe({'project-dir': test_project})
        self.recipe.install()
        self.assertIn(os.path.join(self.buildout_dir, test_project),
                      self.script_cat('manage'))

    @mock.patch('zc.recipe.egg.egg.Scripts.working_set',
                return_value=(None, []))
    def test_create_manage_script_with_initialization(self, working_set):
        # When an init code is specified, it should be added to the script
        self.init_recipe({'initialization': 'import os\nassert True'})
        self.recipe.install()
        self.assertIn('import os\nassert True\n\nimport djangorecipebook',
                      self.script_cat('manage'))
