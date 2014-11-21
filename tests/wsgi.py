import os
import sys
import mock
import logging
import tempfile
import shutil

from testfixtures import log_capture

from ._base import ScriptTests, RecipeTests, test_settings

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

    @mock.patch.dict(os.environ, clear=True)
    @mock.patch('zc.recipe.egg.egg.Scripts.working_set',
                return_value=(None, []))
    @log_capture(level=logging.ERROR)
    def test_virtualenv_no_workon_home(self, working_set, lcapt):
        self.init_recipe({'virtualenv': 'myvenv'})
        self.recipe.install()
        lcapt.check(('wsgi', 'ERROR',
            "The 'virtualenv' option is set in part [wsgi] while "
            "no WORKON_HOME environment variable is available. "
            "Part [wsgi] will be installed in the global python "
            "environment."))

    @mock.patch('zc.recipe.egg.egg.Scripts.working_set',
                return_value=(None, []))
    @log_capture(level=logging.ERROR)
    def test_virtualenv_non_existent_venv(self, working_set, lcapt):
        workon_home = tempfile.mkdtemp('workon_home')
        try:
            with mock.patch.dict(os.environ, WORKON_HOME=workon_home):
                self.init_recipe({'virtualenv': 'myvenv'})
                self.recipe.install()

                lcapt.check(('wsgi', 'ERROR',
                    "part [wsgi]: no virtualenv named 'myvenv' is available "
                    "on this system. Please create it or update the "
                    "virtualenv option."))
        finally:
            shutil.rmtree(workon_home)

    @mock.patch('zc.recipe.egg.egg.Scripts.working_set',
                return_value=(None, []))
    @log_capture(level=logging.ERROR)
    def test_virtualenv_activate_this_not_found(self, working_set, lcapt):
        workon_home = tempfile.mkdtemp('workon_home')
        bin_dir = 'Scripts' if sys.platform == 'win32' else 'bin'
        bin_path = os.path.join(workon_home, 'myvenv', bin_dir)
        os.makedirs(bin_path)
        try:
            with mock.patch.dict(os.environ, WORKON_HOME=workon_home):
                self.init_recipe({'virtualenv': 'myvenv'})
                self.recipe.install()

                lcapt.check(('wsgi', 'ERROR',
                    "part [wsgi], option virtualenv: activate_this.py "
                    "was not found in %s." % bin_path))

        finally:
            shutil.rmtree(workon_home)

    @mock.patch('zc.recipe.egg.egg.Scripts.working_set',
                return_value=(None, []))
    @log_capture(level=logging.ERROR)
    def test_virtualenv(self, working_set, lcapt):
        workon_home = tempfile.mkdtemp('workon_home')
        bin_dir = 'Scripts' if sys.platform == 'win32' else 'bin'
        os.makedirs(os.path.join(workon_home, 'myvenv', bin_dir))
        act_this_file = os.path.join(workon_home, 'myvenv',
                                     bin_dir, 'activate_this.py')
        open(act_this_file, 'w').close()
        try:
            with mock.patch.dict(os.environ, WORKON_HOME=workon_home):
                self.init_recipe({'virtualenv': 'myvenv'})
                self.recipe.install()
                self.assertIn("activate_this = r'%s'\n"
                              "execfile(activate_this, "
                              "dict(__file__=activate_this))" % act_this_file,
                              self.script_cat('wsgi'))
        finally:
            shutil.rmtree(workon_home)
