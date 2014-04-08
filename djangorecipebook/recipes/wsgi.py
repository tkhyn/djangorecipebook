"""
Recipe generating a wsgi script
"""

# derived from R van Laar's djangorecipe

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

venv_setup = '''
activate_this = r'%s'
execfile(activate_this, dict(__file__=activate_this))
'''


class Recipe(BaseRecipe):

    def __init__(self, buildout, name, options):
        super(Recipe, self).__init__(buildout, name, options)
        options.setdefault('log-file', '')

        if options['log-file']:
            loglevel = options.get('log-level', 'INFO')
            if loglevel not in ('INFO', 'ERROR'):
                raise ValueError('log-level should be INFO or ERROR')
            options['log-level'] = str(getattr(logging, loglevel))

        options.setdefault('virtualenv', '')

    def install(self):
        __, working_set = self.egg.working_set(['djangorecipebook'])

        venv = self.options['virtualenv']
        workon_home = os.environ.get('WORKON_HOME', '')
        venv_path = ''

        if venv:
            if workon_home:
                envs = os.listdir(workon_home)
                if venv in envs:
                    bin_dir = 'Scripts' if sys.platform == 'win32' else 'bin'
                    venv_path = os.path.join(workon_home, venv,
                                             bin_dir, 'activate_this.py')
                    if not os.path.isfile(venv_path):
                        logging.getLogger(self.name).error(
                            "part [%s], option virtualenv: activate_this.py "
                            "was not found in %s." %
                            (self.name, os.path.dirname(venv_path)))
                else:
                    logging.getLogger(self.name).error(
                        "part [%s]: no virtualenv named '%s' is available on "
                        "this system. Please create it or update the "
                        "virtualenv option." % (self.name, venv))
            else:
                logging.getLogger(self.name).error(
                    "The 'virtualenv' option is set in part [%(part)s] while "
                    "no WORKON_HOME environment variable is available. "
                    "Part [%(part)s] will be installed in the global python "
                    "environment." % {'part': self.name})

        _script_template = easy_install.script_template
        easy_install.script_template = easy_install.script_header + \
            ((venv_setup % venv_path) if venv_path else '') + \
            wsgi_template

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
