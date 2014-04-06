import os
import sys
import mock
import logging
import tempfile

from base import ScriptTests, RecipeTests, test_settings

from djangorecipebook.scripts.wsgi import main
from djangorecipebook.recipes.wsgi import Recipe


class WSGIScriptTests(ScriptTests):

    @mock.patch('django.core.wsgi.get_wsgi_application')
    @mock.patch('os.environ', {'DJANGO_SETTINGS_MODULE': test_settings})
    def test_script(self, mock_wsgiapp):
        # ^^^ Our regular os.environ.setdefault patching doesn't help.
        # Patching get_wsgi_application already imports the DB layer, so the
        # settings are already needed there!
        main(test_settings)
        self.assertTrue(mock_wsgiapp.called)

    @mock.patch('django.core.wsgi.get_wsgi_application')
    @mock.patch('os.environ', {'DJANGO_SETTINGS_MODULE': test_settings})
    def test_logger(self, mock_wsgiapp):
        fd, logfile = tempfile.mkstemp('.log')
        os.close(fd)
        log_test_string = 'This is a test log'
        main(test_settings, logfile=logfile)

        # test that the file has been created
        self.assertTrue(os.path.exists(logfile))

        # test that the logger does its job
        print(log_test_string)
        sys.stdout.write(log_test_string)
        f = open(logfile, 'r')
        self.assertIn(log_test_string, f.read())
        f.close()

        # close handler and remove temporary log file
        logger = logging.getLogger('wsgi_outerr_logger')
        handler = logger.handlers[0]
        logger.removeHandler(handler)
        handler.flush()
        handler.close()
        os.remove(logfile)


class WSGIRecipeTests(RecipeTests):

    recipe_class = Recipe
    recipe_name = 'wsgi'
    recipe_options = {'recipe': 'djangorecipebook:wsgi'}

    @mock.patch('zc.recipe.egg.egg.Scripts.working_set',
                return_value=(None, []))
    def test_make_wsgi_script_default(self, working_set):
        # Default install of a WSGI script, check that the code creating the
        # wsgi application is generated
        self.recipe.install()
        wsgi_script = self.script_path('wsgi')
        self.assertTrue(os.path.exists(wsgi_script))
        self.assertIn("application = " \
                      "djangorecipebook.scripts.wsgi.main('%s')" % \
                      test_settings,
                      self.script_cat(wsgi_script))

    @mock.patch('zc.recipe.egg.egg.Scripts.working_set',
                return_value=(None, []))
    def test_contents_wsgi_script_initialization(self, working_set):
        # When an init code is specified, it should be added to the script
        self.init_recipe({'initialization': 'import os\nassert True'})
        self.recipe.install()
        self.assertIn('import os\nassert True\n\nimport djangorecipebook',
                      self.script_cat('wsgi'))

    @mock.patch('zc.recipe.egg.egg.Scripts.working_set',
                return_value=(None, []))
    def test_contents_log_wsgi_script(self, working_set):
        # tests that the scripts generates logging arguments
        self.init_recipe({'log-file': 'wsgi.log', 'log-level': 'ERROR'})
        self.recipe.install()
        self.assertIn("logfile='wsgi.log', level=%d" % logging.ERROR,
                      self.script_cat('wsgi'))

    def test_logger_wsgi_script_level(self):
        # tests that an exception is risen when bad log level is selected
        with self.assertRaises(ValueError):
            self.init_recipe({'log-file': 'wsgi.log', 'log-level': 'DEBUG'})
