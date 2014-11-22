"""
Recipe generating a script to generate migrations
"""

from django.core.exceptions import ImproperlyConfigured

from .manage import AppsRecipe


class Recipe(AppsRecipe):

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

        if 'south' in self.options:
            args += ", use_south=True"

        return args
