"""
Recipe generating a test script
"""

import os

from .manage import AppsRecipe


class Recipe(AppsRecipe):

    command = 'test'

    def __init__(self, buildout, name, options):
        super(Recipe, self).__init__(buildout, name, options)

        self.script_path = 'djangorecipebook.scripts.pytest'

        workingdir = options.get('workingdir', '')
        if workingdir:
            workingdir = os.path.normpath(workingdir).replace('\\', '\\\\')
        options['workingdir'] = workingdir

    def _packages(self):
        pkgs = super(Recipe, self)._packages()
        pkgs.append('djangorecipebook[pytest]')
        return pkgs

    def _arguments(self):
        return ', '.join(["'%s'" % arg for arg in self.options_to_list('args')])

    def _initialization(self):
        init = super(Recipe, self)._initialization()

        if self.options['workingdir']:
            init += "\nos.chdir('%s')\nsys.path.append(os.getcwd())" % \
                    self.options['workingdir']

        if init and 'import os' not in init:
            init = 'import os\n' + init

        return init
