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

   Creates a script that runs test with a django test runner
