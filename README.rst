djangorecipebook
================

|copyright| 2014 Thomas Khyn

Buildout recipes for django development


About
-----

The recipes available in djangorecipebook are mostly derived from
djangorecipe_'s functionalities. However, while djangorecipe aims at generating
all scripts in one part, djangorecipebook enables you to define one part per
script (create, manage, wsgi, test), hence allowing the use of different
settings and/or eggs for each part.


Available recipes
-----------------

djangorecipebook:manage
   Creates a management script for the project

djangorecipebook:wsgi
   Creates a wsgi script for the project

djangorecipebook:fcgi
   Creates a fcgi script for the project

djangorecipebook:test
   Creates a script that invokes ``manage.py test [apps]``

djangorecipebook:create
   Creates a django project from on a user-defined template or using django's
   ``startproject`` management command. This recipe will not generate any script.
   The name of the created project is the name of the section.


Options
-------

Common options
..............

project-dir
   The directory where the project files lie, relative to the buildout.cfg
   directory.

   Defaults to ``'.'`` (buildout directory).

settings
   The settings module to load, imported from the project directory.

   Defaults to ``'settings'``.

extra-paths
   Paths to add to sys.path in the generated script.

   Defaults to ``[]``.

initialization
   Some (basic) python initialization code to insert in the generated script.
   Don't forget that leading whitespaces are stripped.

   Defaults to ``''``.


WSGI and FCGI options
.....................

log-file
   The path to a log file where all stdout and/or stderr data should be
   redirected to.

   Defaults to ``''``, which disables logging

log-level
   The level to log errors for. Can be one of INFO (stdout + stderr) or
   ERROR (stderr only).

   Defaults to ``INFO``.

virtualenv
   The virtualenv that should be used to run the wsgi/fcgi script. This
   requires virtualenv **and** virtualenvwrapper, as it relies upon the
   ``WORKON_HOME`` environment variable.

   Defaults to ``''``, which disables any virtual environment setup.

Test options
............

apps
   The names of the apps that should be tested, separated by spaces or
   line-breaks. If it is empty, tests will run for all the apps in
   ``INSTALLED_APPS``.

   Defaults to ``''`` (all apps)

Create options
..............

In create mode, the following common options are unused:

- extra-paths
- initialization

The settings import path must be set as it is used to determine whether the
project has already been created or not.

The following options are added:

template-dirs
   The directories in which to search for user-defined project templates. This
   option may also be added in a ``[djangorecipebook]`` section (for example in
   the default.cfg file). See the `Templates discovery`_ section below.

   Defaults to the built-in templates directory, containing default django
   project templates.

template
   The template that should be used.

   Defaults to the standard django project for the major version of django you
   are using.

secret
   The ``SECRET_KEY`` to be used in the created settings file(s).

   Defaults to a randomly generated alphanumeric key.

For more details on templating, see the `Templates`_ section below.


Templates
---------

In create mode, a templating engine is available for greater personalisation
of your django project initialisation.

Templates discovery
...................

If a `template-dirs` option is found either in the recipe section or in a
specific `djangorecipebook` section, the recipe searches in these directories
- from the last defined to the first - for a subdirectory name matching the
`template` name provided.

If the search is unsuccessful or if none of `template-dirs` or `template` are
defined, the recipe uses the default template for the major version of django
being used.

For example, if in ~/.buildout/default.cfg you have the following lines::

    [djangorecipebooks]
    template-dirs =
      /my/project/template/directory
      /my/project/template/directory2

And your buildout.cfg contains this section::

    [mynewproject]
    recipe = djangorecipebook:create
    template-dirs = /my/other/template/dir
    template = mytemplate

The recipe will search for a ``mytemplate`` directory in that order:

1. /my/other/template/dir
2. /my/project/template/directory2
3. /my/project/template/directory

Template engine
...............

The template engine is as simple as it can be and relies upon pythons's
``string.Template``. A variable can be inserted in any file or directory name or
file content in template directory using the syntax ``${variable}``.

The following variables are available:

- any user-defined recipe option from the configuration file
- ``secret``: the secret key for django settings
- ``project_name``: the project name (= the section name)
- ``year``: the current year
- ``month``: the current month
- ``day``: the current day of the month

For example, if you have in buildout.cfg::

    [mynewproject]
    recipe = djangorecipebook:create
    template = mytemplate
    author = Thomas Khyn

for a copyright notice in a module docstring, you may use::

    (c) ${year} ${author}

which will produce to the following output in the final file (if we are in
2014)::

    (c) 2014 Thomas Khyn

or, if you have a directory named ``${project_name}_parameters``, the final name
will be ``mynewproject_parameters``.


.. |copyright| unicode:: 0xA9
.. _djangorecipe: https://github.com/rvanlaar/djangorecipe
