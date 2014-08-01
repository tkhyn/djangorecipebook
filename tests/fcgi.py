# just check FCGI specific features here, all the function relative to
# production scripts generation is tested with WSGI

import os
import mock

from .base import ScriptTests, RecipeTests, test_settings

from djangorecipebook.scripts.fcgi import  main
from djangorecipebook.recipes.fcgi import Recipe


class WSGIScriptTests(ScriptTests):

    @mock.patch('django.core.servers.fastcgi.runfastcgi')
    @mock.patch('os.environ', {'DJANGO_SETTINGS_MODULE': test_settings})
    def test_script(self, mock_fcgi):
        # ^^^ Our regular os.environ.setdefault patching doesn't help.
        # Patching get_wsgi_application already imports the DB layer, so the
        # settings are already needed there!
        main(test_settings)
        self.assertTrue(mock_fcgi.called)
        mock_fcgi.assert_called_with(method="threaded", daemonize="false")


class WSGIRecipeTests(RecipeTests):

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
