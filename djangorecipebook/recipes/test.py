"""
Recipe generating a test script
"""

import sys

from zc.buildout import easy_install

from base import BaseRecipe


class Recipe(BaseRecipe):

    def __init__(self, buildout, name, options):
        super(Recipe, self).__init__(buildout, name, options)
        self.apps = options.get('apps', '').split()

    def install(self):
        __, working_set = self.egg.working_set(['djangorecipebook'])
        if self.apps:
            apps = ', %s' % ', '.join(["'%s'" % app for app in self.apps])
        else:
            apps = ''
        return easy_install.scripts(
            [(self.name, __name__.replace('recipes', 'scripts'), 'main')],
            working_set, sys.executable, self.bin_dir,
            extra_paths=self.extra_paths,
            arguments="'%s'%s" % (self.settings, apps),
            initialization=self.init)

    def update(self):
        self.install()
