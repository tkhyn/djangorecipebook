"""
Defines the base recipe for all recipes of the recipe book
"""

import os
from zc.recipe.egg import Egg


class BaseRecipe(object):

    def __init__(self, buildout, name, options):

        # recipe book's egg
        self.egg = Egg(buildout, options['recipe'].split(':')[0], options)
        self.name = name
        self.buildout = buildout

        root_dir = self.buildout['buildout']['directory']

        # extraction of buildout parameters
        self.bin_dir = self.buildout['buildout']['bin-directory']

        # extraction of common options
        proj_dir = options.get('project-dir', '.')
        self.proj_dir = os.path.normpath(os.path.join(root_dir, proj_dir))
        self.settings = options.get('settings', 'settings')
        self.init = options.get('initialization', '')

        extra_paths = [root_dir]
        if proj_dir != '.':
            extra_paths.append(self.proj_dir)
        for path in options.get('extra-paths', '').splitlines():
            path = path.strip()
            if path:
                extra_paths.append(os.path.normpath(path))
        self.extra_paths = extra_paths
