"""
General tests that concern all recipes
"""

import os
import sys
import mock

from ._base import RecipeTests, test_project

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
        to_find_in = os.path.join(self.buildout_dir, test_project)
        if sys.platform == 'win32' and sys.version_info >= (3, 4):
            to_find_in = to_find_in.lower()
        self.assertIn(to_find_in,
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
        self.assertIn('import os\nassert True\n\n'
                      'added_settings = {}\n\n'
                      'import djangorecipebook',
                      self.script_cat('manage'))

    @mock.patch('zc.recipe.egg.egg.Scripts.working_set',
                return_value=(None, []))
    def test_create_manage_script_with_args(self, working_set):
        # Default install of a test script, check that the call to
        # djangorecipebook.test.main is present and has the apps names in the
        # arguments
        args = ('-v', '--no-input')
        self.init_recipe({'args': '\n    '.join(args)})
        self.recipe.install()
        manage_script = self.script_path('manage')
        script_cat = self.script_cat(manage_script)
        self.assertIn("djangorecipebook.scripts.manage.main(added_settings, %s)"
                      % ', '.join(["'%s'" % arg for arg in args]), script_cat)
        self.assertIn('added_settings = {', script_cat)

    @mock.patch('zc.recipe.egg.egg.Scripts.working_set',
                return_value=(None, []))
    def test_create_manage_script_with_envvars(self, working_set):
        # Install of a test script with custom environment variables
        self.init_recipe({'envvars': 'MYENVVAR = value'})
        self.recipe.install()
        manage_script = self.script_cat('manage')
        self.assertIn('import os', manage_script)
        self.assertIn("os.environ['MYENVVAR'] = 'value'", manage_script)
