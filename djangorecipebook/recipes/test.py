"""
Recipe generating a test script
"""

from .manage import Recipe as ManageRecipe


class Recipe(ManageRecipe):

    def __init__(self, buildout, name, options):
        super(Recipe, self).__init__(buildout, name, options)

        options.setdefault('apps', '')
        options['nose'] = '1' if 'nose' in options else ''
        options.setdefault('workingdir', '')

    def _packages(self):
        pkgs = ['djangorecipebook']
        if self.options['nose']:
            pkgs.append('djangorecipebook[nose]')
        return pkgs


    def _initialization(self):
        init = super(Recipe, self)._initialization()

        if self.options['workingdir']:
            init = "os.chdir('%s')\nsys.path.append(os.getcwd())" % \
                   self.options['workingdir']

        if init and not 'import os' in init:
            init = 'import os\n' + init

        return init

    def _arguments(self):
        """
        Adds the apps to the arguments
        """
        args = super(Recipe, self)._arguments()

        for app in self.options_to_list('apps'):
            args += ", '%s'" % app

        return args
