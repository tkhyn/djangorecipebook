# just check FCGI specific features here, all the function relative to
# production scripts generation is tested with WSGI

import os
import sys
import mock

from ._base import ScriptTests, RecipeTests, test_settings

from djangorecipebook.scripts.fcgi import  main
from djangorecipebook.recipes.fcgi import Recipe


class FCGIScriptTests(ScriptTests):

    @mock.patch('django.core.servers.fastcgi.runfastcgi')
    @mock.patch('os.environ', {'DJANGO_SETTINGS_MODULE': test_settings})
    def test_script(self, mock_fcgi):
        # ^^^ Our regular os.environ.setdefault patching doesn't help.
        # Patching get_wsgi_application already imports the DB layer, so the
        # settings are already needed there!
        main(test_settings)
        self.assertTrue(mock_fcgi.called)
        mock_fcgi.assert_called_with(method="threaded", daemonize="false")


class FCGIRecipeTests(RecipeTests):

    recipe_class = Recipe
    recipe_name = 'fcgi'
    recipe_options = {'recipe': 'djangorecipebook:fcgi'}

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
        fcgi_script = self.script_path('fcgi')
        self.assertTrue(os.path.exists(fcgi_script))
        self.assertIn("djangorecipebook.scripts.fcgi.main('%s')" % \
                      test_settings,
                      self.script_cat(fcgi_script))

    @mock.patch('zc.recipe.egg.egg.Scripts.working_set',
                return_value=(None, []))
    def test_script_path(self, working_set):
        # Check that the script is installed in the provided custom script path
        # instead of the bin directory
        self.init_recipe({'script_path': 'fcgi/app.fcgi'})
        self.recipe.install()
        self.assertTrue(os.path.exists(os.path.join(self.buildout_dir,
                                                   'fcgi/app.fcgi')))
        if sys.platform == 'win32':
            self.assertFalse(os.path.exists(os.path.join(self.bin_dir,
                                                         'fcgi-script.py')))
            self.assertFalse(os.path.exists(os.path.join(self.bin_dir,
                                                         'fcgi.exe')))
        else:
            self.assertFalse(os.path.exists(os.path.join(self.bin_dir,
                                                         'fcgi')))
