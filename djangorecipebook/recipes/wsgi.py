"""
Recipe generating a wsgi script
"""

# largely derived from R van Laar's djangorecipe

import os
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
        self.logfile = options.get('log-file', None)

        if self.logfile:
            loglevel = options.get('log-level', 'INFO')
            if loglevel not in ('INFO', 'ERROR'):
                raise ValueError('log-level should be INFO or ERROR')
            self.loglevel = getattr(logging, loglevel)
        else:
            self.loglevel = None

    def install(self):
        __, working_set = self.egg.working_set(['djangorecipebook'])

        _script_template = easy_install.script_template
        easy_install.script_template = \
            easy_install.script_header + wsgi_template

        logfile = (", logfile='%s'" % self.logfile) if self.logfile else ''
        loglevel = (", level=%d" % self.loglevel) if self.loglevel else ''

        script = easy_install.scripts(
            [(self.name, __name__, 'main')],
            working_set, sys.executable, self.bin_dir,
            extra_paths=self.extra_paths,
            arguments="'%s'%s%s" % (self.settings, logfile, loglevel),
            initialization=self.init)

        easy_install.script_template = _script_template

        return script

    def update(self):
        self.install()


def main(settings_file, logfile=None, level=logging.INFO):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_file)

    if logfile:
        # setup logging
        class StdStrLogger(object):
            def __init__(self, logger, level):
                self.logger = logger
                self.log_level = level

            def write(self, data):
                for line in data.rstrip().splitlines():
                    self.logger.log(self.log_level, line.rstrip())

        logging.basicConfig(
           level=level,
           format='%(asctime)s:%(levelname)s:%(message)s',
           datefmt='%Y%m%d %H:%M:%S',
           filename=logfile,
           filemode='a'
        )

        sys.stdout = StdStrLogger(logging.getLogger('stdout'), logging.INFO)
        sys.stderr = StdStrLogger(logging.getLogger('stdout'), logging.ERROR)

    # Run WSGI handler for the application
    from django.core.wsgi import get_wsgi_application
    return get_wsgi_application()
