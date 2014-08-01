"""
General tests that concern all recipes
"""

import os
import mock

from .base import RecipeTests, test_project

# we use the very simple manage.Recipe to test BaseRecipe functionalities
from djangorecipebook.recipes import manage


class GeneralRecipeTests(RecipeTests):

    recipe_class = manage.Recipe
    recipe_name = 'manage'
    recipe_options = {'recipe': 'djangorecipebook:manage'}

    @mock.patch('zc.recipe.egg.egg.Scripts.working_set',
                return_value=(None, []))
    def test_create_script_projectdir(self, working_set):
        # When a project dir is specified, it should be added to sys.path
        self.init_recipe({'project-dir': test_project})
        self.recipe.install()
        self.assertIn(os.path.join(self.buildout_dir, test_project),
                      self.script_cat('manage'))

    @mock.patch('zc.recipe.egg.egg.Scripts.working_set',
                return_value=(None, []))
    def test_create_script_extra_paths(self, working_set):
        # When extra paths are specified, they should be added to sys.path
        # we use relative paths so that the test is valid on any platform
        extra_paths = ('my/first/extra/path', 'my/second/extra/path')
        # mimick buildout.cfg file formatting
        self.init_recipe({'extra-paths': '\n    '.join(extra_paths)})
        self.recipe.install()
        manage_script = self.script_cat('manage')
        for p in extra_paths:
            self.assertIn(os.path.normpath(p), manage_script)

    @mock.patch('zc.recipe.egg.egg.Scripts.working_set',
                return_value=(None, []))
    def test_create_manage_script_with_initialization(self, working_set):
        # When an init code is specified, it should be added to the script
        self.init_recipe({'initialization': 'import os\nassert True'})
        self.recipe.install()
        self.assertIn('import os\nassert True\n\nimport djangorecipebook',
                      self.script_cat('manage'))
