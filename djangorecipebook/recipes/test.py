"""
Recipe generating a test script
"""

import re

from .manage import Recipe as ManageRecipe


class Recipe(ManageRecipe):

    def __init__(self, buildout, name, options):
        super(Recipe, self).__init__(buildout, name, options)
        options.setdefault('apps', '')
        options.setdefault('workingdir', '')

    def _arguments(self):
        """
        Returns the list of arguments for the djangorecipebook script
        """
        args = super(Recipe, self)._arguments()
        if self.options['apps']:
            for app in re.split('\s+', self.options['apps']):
                args += ", '%s'" % app

        return args

    def _initialization(self):
        init = super(Recipe, self)._initialization()

        if self.options['workingdir']:
            init = "os.chdir('%s')\nsys.path.append(os.getcwd())" % \
                   self.options['workingdir']

        if init and not 'import os' in init:
            init = 'import os\n' + init

        return init
