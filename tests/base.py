# Most of the djangorecipebook's tests were taken from djangorecipe,
# (c) Roland van Laar, BSD license, [https://github.com/rvanlaar/djangorecipe]
# and were simply adapted to the needs of djangorecipebook


__test__ = False

import sys
import os
import shutil
import tempfile
import unittest
import mock


test_project = 'project'
test_settings = 'settings'


is_win32 = sys.platform == 'win32'


class ScriptTests(unittest.TestCase):

    def setUp(self):
        # fake the settings file's module
        self.settings = mock.sentinel.Settings
        self.settings.SECRET_KEY = 'I mock your secret key'
        sys.modules[test_project] = mock.sentinel.CheeseShop
        sys.modules[test_project + '.' + test_settings] = self.settings
        setattr(sys.modules[test_project], test_settings, self.settings)
        print("DJANGO ENV: %s" % os.environ.get('DJANGO_SETTINGS_MODULE'))

    def tearDown(self):
        # We will clear out sys.modules again to clean up
        for m in [test_project, test_project + '.' + test_settings]:
            del sys.modules[m]


class RecipeTests(unittest.TestCase):

    recipe_class = None
    recipe_name = ''
    recipe_options = {}

    def setUp(self):
        # Create a directory for our buildout files created by the recipe
        self.buildout_dir = tempfile.mkdtemp('djangorecipebook')

        self.bin_dir = os.path.join(self.buildout_dir, 'bin')
        self.develop_eggs_dir = os.path.join(self.buildout_dir, 'develop-eggs')
        self.eggs_dir = os.path.join(self.buildout_dir, 'eggs')
        self.parts_dir = os.path.join(self.buildout_dir, 'parts')

        # We need to create the bin and eggs dir since the recipe expects
        # them to exist
        os.mkdir(self.bin_dir)
        os.mkdir(self.eggs_dir)

        self.init_recipe()

    def init_recipe(self, options={}, name=None):
        self.recipe = self.recipe_class(
            {'buildout': {
                'eggs-directory': self.eggs_dir,
                'develop-eggs-directory': self.develop_eggs_dir,
                'bin-directory': self.bin_dir,
                'parts-directory': self.parts_dir,
                'directory': self.buildout_dir,
                'python': 'buildout',
                'executable': sys.executable,
                'find-links': '',
                'allow-hosts': ''},
             },
             name or self.recipe_name,
             dict(self.recipe_options, **options)
        )

    def tearDown(self):
        # Remove our test dir
        shutil.rmtree(self.buildout_dir)

    def script_path(self, *names):
        """
        Gets the path to a script, adding the -script.py suffix if necessary
        """
        path = os.path.join(self.bin_dir, *names)
        if is_win32 and not os.path.exists(path):
            path_win = path + '-script.py'
            if os.path.exists(path_win):
                path = path_win
        return path

    def script_cat(self, *names):
        """
        Reads a script file, adding the -script.py suffix if necessary
        """
        path = self.script_path(self.bin_dir, *names)
        return open(path).read().replace('\\\\', '\\')
