# The basic djangorecipebook tests were taken from djangorecipe,
# (c) Roland van Laar, BSD license, [https://github.com/rvanlaar/djangorecipe]
# and were simply adapted to the needs of djangorecipebook


__test__ = False

import sys
import os
import shutil
import tempfile
import mock

try:
    import unittest2 as unittest  # for python 2.6
except ImportError:
    import unittest

from zc.buildout.testing import TestOptions


test_project = 'project'
test_settings = 'settings'


is_win32 = sys.platform == 'win32'


class ScriptTests(unittest.TestCase):

    def setUp(self):
        # fake the settings file's module
        self.settings = mock.sentinel.Settings
        sys.modules[test_settings] = self.settings

    def tearDown(self):
        # We will clear out sys.modules again to clean up
        del sys.modules[test_settings]


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

        buildout_obj = {'buildout': {
            'eggs-directory': self.eggs_dir,
            'develop-eggs-directory': self.develop_eggs_dir,
            'bin-directory': self.bin_dir,
            'parts-directory': self.parts_dir,
            'directory': self.buildout_dir,
            'allow-hosts': '',  # don't visit any URL
            'find-links': '',
            'python': 'buildout',
            'executable': sys.executable,
        }}

        name = name or self.recipe_name
        options_obj = TestOptions(buildout_obj, name,
                                  dict(self.recipe_options, **options))

        self.recipe = self.recipe_class(buildout_obj, name, options_obj)

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
