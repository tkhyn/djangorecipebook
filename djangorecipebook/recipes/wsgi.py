"""
Recipe generating a wsgi script
"""

# largely derived from R van Laar's djangorecipe

import sys
import logging

from base import BaseRecipe
from zc.buildout import easy_install


wsgi_template = """

%(relative_paths_setup)s
import sys
sys.path[0:0] = [
  %(path)s,
  ]
%(initialization)s
import %(module_name)s

application = %(module_name)s.%(attrs)s(%(arguments)s)
"""


class Recipe(BaseRecipe):

    def __init__(self, buildout, name, options):
        super(Recipe, self).__init__(buildout, name, options)
        options.setdefault('log-file', '')

        if options['log-file']:
            loglevel = options.get('log-level', 'INFO')
            if loglevel not in ('INFO', 'ERROR'):
                raise ValueError('log-level should be INFO or ERROR')
            options['log-level'] = str(getattr(logging, loglevel))

    def install(self):
        __, working_set = self.egg.working_set(['djangorecipebook'])

        _script_template = easy_install.script_template
        easy_install.script_template = \
            easy_install.script_header + wsgi_template

        if self.options['log-file']:
            logfile = (", logfile='%s'" % self.options['log-file'])
            loglevel = (", level=%s" % self.options['log-level'])
        else:
            logfile = loglevel = ''

        script = easy_install.scripts(
            [(self.name, __name__.replace('recipes', 'scripts'), 'main')],
            working_set, sys.executable, self.options['bin_dir'],
            extra_paths=self.options['extra-paths'].split(';'),
            arguments="'%s'%s%s" % (self.options['settings'],
                                    logfile, loglevel),
            initialization=self.options['initialization'])

        easy_install.script_template = _script_template

        return script

    def update(self):
        self.install()
