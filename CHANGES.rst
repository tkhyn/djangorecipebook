Changes
=======

1.2 (dev)
---------

- Django 1.7 is now the officially supported Django release
- Added ``makemigrations`` recipe that supports Django 1.7 and south migrations

1.1 (2014-08-03)
----------------

- Added ``nose`` and ``workingdir`` options to ``test`` recipe, to install
  and run with django_nose_ and select the base directory for the test modules
- Added ``args`` option to ``manage`` and ``test`` recipes to provide
  supplementary command line arguments
- Added ``envvar`` option to all recipes to set environment variables

1.0 (2014-08-02)
----------------

- Supports Django 1.4 to 1.7, and relevant python versions (2.6 to 3.4)


0.2.1 (2014-07-20)
------------------

- Added virtualenv option in wsgi recipe
- Added fcgi recipe
- Fixed settings issue when using --settings argument


0.2 (2014-04-08)
----------------

- Added create recipe and templating engine
- Added bootstrap.py
- Removed script-name option (from docs, as it was not implemented)


0.1 (2014-04-05)
----------------

- Initial version. Manage, test and wsgi recipes implemented

0.0 (2014-04-04)
----------------

- Birth


.. _django_nose: https://pypi.python.org/pypi/django-nose
