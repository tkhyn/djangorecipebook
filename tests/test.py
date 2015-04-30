import os
import mock

from ._base import RecipeTests

from djangorecipebook.recipes.test import Recipe


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
        self.assertIn(
            "djangorecipebook.scripts.manage.main(added_settings, 'test')",
            self.script_cat(test_script)
        )

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
        self.assertIn(
            "djangorecipebook.scripts.manage.main(added_settings, 'test', %s)"
            % ', '.join(["'%s'" % app for app in apps]),
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
