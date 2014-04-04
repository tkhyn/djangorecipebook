"""
Recipe generating a management script
"""

import os
import sys

from base import BaseRecipe
from zc.buildout import easy_install


class Recipe(BaseRecipe):

    def install(self):
        __, working_set = self.egg.working_set()
        return easy_install.scripts(
            [(self.name, __name__, 'main')],
            working_set, sys.executable, self.bin_dir,
            extra_paths=self.extra_paths,
            arguments="'%s'" % self.settings,
            initialization=self.init)


def main(settings_module):
    # called on script execution
    from django.core import management
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
    management.execute_from_command_line(sys.argv)
