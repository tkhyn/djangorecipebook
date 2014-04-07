import os
import tempfile
import shutil
from datetime import date

from base import RecipeTests

from djangorecipebook.recipes.create import Recipe


class CreateRecipeTests(RecipeTests):

    recipe_class = Recipe
    recipe_name = 'create'
    recipe_options = {'recipe': 'djangorecipebook:create'}

    def test_consistent_options(self):
        options_1 = self.recipe.options
        self.init_recipe()
        self.assertEqual(options_1, self.recipe.options)

    def test_random_secret(self):
        secrets = []
        for i in range(10):
            s = self.recipe.get_random_secret()
            for sp in secrets:
                self.assertNotEqual(sp, s)
            secrets.append(s)

    def test_install(self):
        # If a project does not exist already the recipe will create
        # a default one using django's startproject management command

        self.recipe.install()

        # the project directory is the root buildout dir by default
        project_dir = self.buildout_dir

        expected_files = ('__init__.py', 'settings.py', 'urls.py', 'wsgi.py')
        self.assertTrue(set(expected_files).issubset(os.listdir(project_dir)))

    def test_templating(self):
        # create a project from a template directory
        project_dir = self.buildout_dir
        temp_dir = tempfile.mkdtemp('templates')
        self.init_recipe({'template': 'template',
                          'template-dirs': temp_dir,
                          'author': 'Thomas Khyn',
                          'app1': 'myapp'})

        temp_path = os.path.join(temp_dir, 'template')
        os.mkdir(temp_path)
        lic = open(os.path.join(temp_path, 'LICENSE.txt'), 'w')
        lic.write('(c) ${year} ${author}')
        lic.close()

        pkg = '${project_name}'
        os.mkdir(os.path.join(temp_path, pkg))

        init = open(os.path.join(temp_path, pkg, '__init__.py'), 'w')
        init.write("AUTHOR = '${author}'")
        init.close()

        app = '${app1}'
        os.mkdir(os.path.join(temp_path, pkg, app))
        init = open(os.path.join(temp_path, pkg, app, '__init__.py'), 'w')
        init.close()

        # fake initialisation of installation
        self.recipe.options._created = []
        self.recipe.install()

        # check files existence
        expected = ('LICENSE.txt', 'create')
        self.assertTrue(set(expected).issubset(os.listdir(project_dir)))
        self.assertTrue(os.path.isdir(os.path.join(project_dir, 'create')))
        self.assertTrue(os.path.isfile(os.path.join(project_dir, 'create',
                                                    '__init__.py')))
        self.assertTrue(os.path.isdir(os.path.join(project_dir, 'create',
                                                   'myapp')))

        # check files content
        year = date.today().year
        lic = open(os.path.join(project_dir, 'LICENSE.txt'), 'r')
        self.assertEqual(lic.read(), '(c) %s Thomas Khyn' % year)
        lic.close()

        module = open(os.path.join(project_dir, 'create', '__init__.py'), 'r')
        self.assertEqual(module.read(), "AUTHOR = 'Thomas Khyn'")
        module.close()

        shutil.rmtree(temp_dir)
