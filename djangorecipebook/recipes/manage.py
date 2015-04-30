"""
Recipe generating a management script
"""

import sys

from zc.buildout import easy_install

from .base import BaseRecipe
from ..exceptions import ImproperlyConfigured


class ManageRecipe(BaseRecipe):

    command = None
    script_path = 'djangorecipebook.scripts.manage'

    def _packages(self):
        return ['djangorecipebook']

    def __init__(self, buildout, name, options):
        options.setdefault('settings', '')
        super(ManageRecipe, self).__init__(buildout, name, options)
        options.setdefault('args', '')

        inst_apps = options.setdefault('inst_apps', '')
        apps = options.get('apps', '')
        self.added_settings = {}
        if inst_apps or apps:
            inst_apps = self.options_to_list('inst_apps')
            apps = self.options_to_list('apps')
            inst_apps.extend(set(apps).difference(inst_apps))
            self.added_settings['INSTALLED_APPS'] = tuple(inst_apps)

    def _arguments(self):
        """
        Returns the list of arguments for the djangorecipebook script
        """
        args = []

        settings = self.options['settings']
        if settings:
            args.append("'%s'" % settings)
        else:
            args.append('added_settings')  # see self._initialization

        if self.command is not None:
            args.append("'%s'" % self.command)

        args += ["'%s'" % arg for arg in self.options_to_list('args')]

        return ', '.join(args)

    def _initialization(self):
        init = super(ManageRecipe, self)._initialization()

        if not self.options['settings']:
            init += '\n\nadded_settings = %s' % repr(self.added_settings)

        return init

    def install(self):
        if self.options['settings'] and self.options['inst_apps']:
            raise ImproperlyConfigured(
                'Cannot define a settings module and a list of installed apps')

        __, working_set = self.egg.working_set(self._packages())
        return easy_install.scripts(
            [(self.name, self.script_path, 'main')],
            working_set, sys.executable, self.options['bin_dir'],
            extra_paths=self.options['extra-paths'].split(';'),
            arguments=self._arguments(),
            initialization=self._initialization())

    def update(self):
        self.install()


class Recipe(ManageRecipe):
    """
    Management recipe with a 'command' option
    """
    def __init__(self, buildout, name, options):
        super(Recipe, self).__init__(buildout, name, options)
        try:
            self.command = options['command']
        except KeyError:
            if options['args']:
                raise ImproperlyConfigured(
                    'You must provide a command if you provide args to the '
                    'manage recipe.')


class AppsRecipe(ManageRecipe):
    """
    A management recipe with an 'apps' option
    """

    def __init__(self, buildout, name, options):
        options.setdefault('apps', '')
        super(AppsRecipe, self).__init__(buildout, name, options)

    def _arguments(self):
        args = super(AppsRecipe, self)._arguments()
        for app in self.options_to_list('apps'):
            args += ", '%s'" % app
        return args
