"""
Recipe generating a test script
"""

import re

from .manage import Recipe as ManageRecipe


class Recipe(ManageRecipe):

    def __init__(self, buildout, name, options):
        super(Recipe, self).__init__(buildout, name, options)
        options.setdefault('apps', '')

    def _arguments(self):
        """
        Returns the list of arguments for the djangorecipebook script
        """
        args = super(Recipe, self)._arguments()
        if self.options['apps']:
            for app in re.split('\s+', self.options['apps']):
                args += ", '%s'" % app

        return args
