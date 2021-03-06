"""
Recipe generating a script for database migration
"""

from .manage import AppsRecipe


class Recipe(AppsRecipe):

    command = 'migrate'

    def __init__(self, buildout, name, options):
        # a settings module is needed, one cannot use minimal settings
        # to migrate a database !
        options.setdefault('settings', 'settings')
        super(Recipe, self).__init__(buildout, name, options)
