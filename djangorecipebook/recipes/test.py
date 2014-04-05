"""
Recipe generating a test script
"""

import os
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
            [(self.name, __name__, 'main')],
            working_set, sys.executable, self.bin_dir,
            extra_paths=self.extra_paths,
            arguments="'%s'%s" % (self.settings, apps),
            initialization=self.init)

    def update(self):
        self.install()


def main(settings_file, *apps):
    from django.core import management
    argv = ['test', 'test'] + list(apps)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_file)
    management.execute_from_command_line(argv)
