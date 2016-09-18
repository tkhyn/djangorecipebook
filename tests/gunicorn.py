# just check gunicorn specific features here, all the function relative to
# production scripts generation is tested with WSGI

import os
import sys
import mock

from ._base import ScriptTests, RecipeTests, test_settings

from djangorecipebook.scripts.gunicorn import main
from djangorecipebook.recipes.gunicorn import Recipe


class GunicornScriptTests(ScriptTests):

    @mock.patch('djangorecipebook.scripts.gunicorn.gunicorn_run')
    @mock.patch('sys.argv', ['./gunicorn'])
    def test_script(self, mock_gunicorn):
        # ^^^ Our regular os.environ.setdefault patching doesn't help.
        # Patching get_wsgi_application already imports the DB layer, so the
        # settings are already needed there!
        main('wsgi:application')
        self.assertTrue(mock_gunicorn.called)
        self.assertListEqual(sys.argv, ['./gunicorn', 'wsgi:application'])
        mock_gunicorn.assert_called_with()


class GunicornRecipeTests(RecipeTests):

    recipe_class = Recipe
    recipe_name = 'gunicorn'
    recipe_options = {'recipe': 'djangorecipebook:gunicorn'}

    def test_consistent_options(self):
        options_1 = self.recipe.options
        self.init_recipe()
        self.assertEqual(options_1, self.recipe.options)

    @mock.patch('zc.recipe.egg.egg.Scripts.working_set',
                return_value=(None, []))
    def test_make_wsgi_script_default(self, working_set):
        # Default install of a WSGI script, check that the code creating the
        # wsgi application is generated
        self.recipe.install()
        gunicorn_script = self.script_path('gunicorn')
        self.assertTrue(os.path.exists(gunicorn_script))
        self.assertIn(
            "djangorecipebook.scripts.gunicorn.main()",
            self.script_cat(gunicorn_script)
        )

    @mock.patch('zc.recipe.egg.egg.Scripts.working_set',
                return_value=(None, []))
    def test_script_path(self, working_set):
        # Check that the auto-wsgi application is also installed
        self.init_recipe({'application': 'auto'})
        self.recipe.install()
        self.assertTrue(os.path.exists(
            os.path.join(self.bin_dir, 'gunicorn_wsgi.py')
        ))
        if sys.platform == 'win32':
            self.assertFalse(os.path.exists(
                os.path.join(self.bin_dir, 'gunicorn_wsgi-script.py')
            ))
            self.assertFalse(os.path.exists(
                os.path.join(self.bin_dir, 'gunicorn_wsgi.exe')
            ))
        else:
            self.assertFalse(os.path.exists(
                os.path.join(self.bin_dir, 'gunicorn')
            ))
        # check that sys.path is not changed in the generated wsgi script
        self.assertNotIn('sys.path[0:0] =',
                         self.script_cat('gunicorn_wsgi.py'))
