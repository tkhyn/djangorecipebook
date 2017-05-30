"""
Recipe generating a script to generate migrations
"""


from .manage import AppsRecipe
from ..exceptions import ImproperlyConfigured


class Recipe(AppsRecipe):

    command = None
    script_path = 'djangorecipebook.scripts.makemigrations'

    def install(self):
        if not any((self.options['settings'], self.options['inst_apps'],
                    self.options['apps'])):
            raise ImproperlyConfigured(
                'You need to provide at least one installed app or a settings '
                'module to generate migrations.')

        return super(Recipe, self).install()
