"""
Recipe generating a management script
"""

import sys
import re

from zc.buildout import easy_install
from django.core.exceptions import ImproperlyConfigured

from .base import BaseRecipe


class Recipe(BaseRecipe):

    def _packages(self):
        return ['djangorecipebook']

    def __init__(self, buildout, name, options):
        settings = options.setdefault('settings', '')
        super(Recipe, self).__init__(buildout, name, options)
        options.setdefault('args', '')

        inst_apps = options.setdefault('inst_apps', '')

        if settings and inst_apps:
            raise ImproperlyConfigured(
                'Cannot define a settings module and a list of installed apps')

        self.added_settings = {}

        if inst_apps:
            self.added_settings['INSTALLED_APPS'] = \
                tuple(self.options_to_list('inst_apps'))

    def _arguments(self):
        """
        Returns the list of arguments for the djangorecipebook script
        """
        args = ''
        if self.options['args']:
            args += ', %s' % ', '.join(
                "'%s'" % d for d in re.split('\s+', self.options['args']))

        settings = self.options['settings']
        if settings:
            settings = "'%s'" % settings
        else:
            settings = 'added_settings'  # see self._initialization

        return "%s%s" % (settings, args)

    def _initialization(self):
        init = super(Recipe, self)._initialization()

        if not self.options['settings']:
            init += '\n\nadded_settings = %s' % repr(self.added_settings)

        return init

    def install(self):
        __, working_set = self.egg.working_set(self._packages())
        script_path = self.__class__.__module__.replace('recipes', 'scripts')
        return easy_install.scripts(
            [(self.name, script_path, 'main')],
            working_set, sys.executable, self.options['bin_dir'],
            extra_paths=self.options['extra-paths'].split(';'),
            arguments=self._arguments(),
            initialization=self._initialization())

    def update(self):
        self.install()
