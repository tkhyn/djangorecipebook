import os
import mock

from ._base import ScriptTests, RecipeTests

from djangorecipebook.scripts.migrate import main
from djangorecipebook.recipes.migrate import Recipe


class TestScriptTests(ScriptTests):

    @mock.patch('sys.argv', ['migrate'])
    @mock.patch('django.core.management.execute_from_command_line')
    def test_script(self, mock_execute):
        main('settings')
        self.assertListEqual(mock_execute.call_args[0][0],
                             ['manage.py', 'migrate', '--settings=settings'])


class MigrateRecipeTests(RecipeTests):

    recipe_class = Recipe
    recipe_name = 'migrate'
    recipe_options = {'recipe': 'djangorecipebook:migrate'}

    @mock.patch('zc.recipe.egg.egg.Scripts.working_set',
                return_value=(None, []))
    def test_install_default_settings(self, working_set):
        self.recipe.install()
        migrate_script = self.script_path('migrate')
        self.assertTrue(os.path.exists(migrate_script))
        self.assertIn("djangorecipebook.scripts.migrate.main('settings')",
                      self.script_cat(migrate_script))
