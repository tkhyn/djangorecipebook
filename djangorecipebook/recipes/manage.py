"""
Recipe generating a management script
"""

import sys

from base import BaseRecipe
from zc.buildout import easy_install


class Recipe(BaseRecipe):

    def install(self):
        __, working_set = self.egg.working_set(['djangorecipebook'])
        return easy_install.scripts(
            [(self.name, __name__.replace('recipes', 'scripts'), 'main')],
            working_set, sys.executable, self.bin_dir,
            extra_paths=self.extra_paths,
            arguments="'%s'" % self.settings,
            initialization=self.init)

    def update(self):
        self.install()
