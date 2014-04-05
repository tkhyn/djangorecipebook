djangorecipebook
================

(c) 2014 Thomas Khyn

Buildout recipes for django development


About
-----

The recipes provided in djangorecipebook are mostly derived from
_djangorecipe's functionalities. However, while djangorecipe aims at generating
all scripts in one part (and therefore one settings module), djangorecipebook
enables you to define one part per script (create, manage, wsgi, test), hence
allowing the use of different settings and eggs for each part.

.. _djangorecipe: https://github.com/rvanlaar/djangorecipe

Available recipes
-----------------

djangorecipebook:manage

   Creates a management script for the project

djangorecipebook:wsgi

   Creates a wsgi script for the project

djangorecipebook:test

   Creates a script that invokes `manage.py test [apps]`


Options
-------

Common options
..............

project-dir
   The directory where the project files lie, relative to the buildout.cfg
   directory.

   Defaults to `'.'` (buildout directory).

settings
   The settings module to load, imported from the project directory.

   Defaults to `'settings'`.

extra-paths
   Paths to add to sys.path in the generated script.

   Defaults to `[]`.

script-name
   The name of the script that should be generated.

   Defaults to the part name.

initialization
   Some (basic) python initialization code to insert in the generated script.
   Don't forget that leading whitespaces are stripped.

   Defaults to none.


WSGI options
............

log-file
   The path to a log file where all stdout and/or stderr data should be
   redirected to.

   Defaults to `None`, which disables logging

log-level
   The level to log errors for. Can be one of INFO (stdout + stderr) or
   ERROR (stderr only).

   Defaults to `INFO`.

Test options
............

apps
   The names of the apps that should be tested, separated by spaces or
   line-breaks. If it is empty, tests will run for all the apps in
   `INSTALLED_APPS`.

   Defaults to `` (all apps)
