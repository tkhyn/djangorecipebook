import os
import mock

from ._base import RecipeTests

from djangorecipebook.recipes.migrate import Recipe


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
        self.assertIn(
            "djangorecipebook.scripts.manage.main('settings', 'migrate')",
            self.script_cat(migrate_script)
        )
