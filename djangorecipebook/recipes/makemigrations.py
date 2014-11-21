"""
Recipe generating a script to generate migrations
"""

from django.core.exceptions import ImproperlyConfigured

from .manage import Recipe as ManageRecipe


class Recipe(ManageRecipe):

    def __init__(self, buildout, name, options):
        super(Recipe, self).__init__(buildout, name, options)
        options.setdefault('apps', '')

    def install(self):
        if not any((self.options['settings'], self.options['inst_apps'],
                    self.options['apps'])):
            raise ImproperlyConfigured(
                'You need to provide at least one installed app or a settings '
                'module to generate migrations.')
        return super(Recipe, self).install()

    def _arguments(self):
        """
        Adds the apps to the arguments
        """
        args = super(Recipe, self)._arguments()
        for app in self.options_to_list('apps'):
            args += ", '%s'" % app

        if 'south' in self.options:
            args += ", use_south=True"

        return args
