"""
Defines the base recipe for all recipes of the recipe book
"""

import os
from zc.recipe.egg import Egg


class BaseRecipe(object):

    def __init__(self, buildout, name, options):

        root_dir = buildout['buildout']['directory']

        # recipe book's egg
        self.egg = Egg(buildout, options['recipe'], options)

        # extraction of buildout parameters
        self.bin_dir = buildout['buildout']['bin-directory']

        # extraction of common options
        proj_dir = options.get('project-dir', '.')
        self.proj_dir = os.path.normpath(root_dir, proj_dir)
        self.settings = options.get('settings', 'settings')
        self.script_name = options.get('script-name', name)
        self.init = options.get('initializiation', '')

        extra_paths = [root_dir]
        if proj_dir != '.':
            extra_paths.append(self.proj_dir)
        for path in self.options.get('extra-paths', '').splitlines():
            path = path.strip()
            if path:
                extra_paths.append(os.path.normpath(path))
