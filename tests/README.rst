djangorecipebook tests
======================

If you are reading this, you're interested in contributing to this software.
Great news!

Before you start playing around, you may need the information that follows.


The tests
---------

djangorecipebook uses nose_ for testing. All the tests are in the ``tests``
directory, and the nose test runner uses the ``all-modules`` option which
is defined in ``setup.cfg``. This means that any object which is not intended
to contain tests (e.g. a base class module) shall contain the statement
``__test__ = False``.

The ``setup.cfg`` file also contains coverage pre-configuration information,
but coverage is disabled by default.


Generating the test scripts
---------------------------

djangorecipebook - surprisingly - uses zc.buildout_ to generate its test
scripts.

To create the ``python`` interpreter and the ``tests`` and ``coverage`` scripts
in the ``bin`` folder, simply run ``buildout`` in the main directory.

You may want to use the ``bootstrap.py`` script to locally install buildout
locally beforehand.


Running the tests
-----------------

Simply generate the test scripts as above and, from the main directory, type::

   $ bin/tests

For coverage information, you can add ``--with-coverage`` to the above test
command but it's more convenient to use the shortcut::

   $ bin/coverage

You may want to run the test suite manually from the command line (to launch
tests from within an IDE, for example). To do this:

   - make sure that all the required dependencies are satisfied in the
     environment you are working in
   - add the main directory (where ``setup.py`` lies) to ``PYTHONPATH``
   - set the working directory to ``tests``

And simply use::

   $ nosetests [options]


Running the tox suite
---------------------

This software uses tox_ to test against various environments.

If you have never heard of tox, it is an automated tool that creates virtual
environments with given python interpreters and/or library versions, and runs
the test suite in each of these environments.

Running the tox suite is just a matter of installing tox and running it from
the main directory::

   $ pip install tox
   $ tox


.. _zc.buildout: http://www.buildout.org/en/latest/
.. _nose: http://nose.readthedocs.org/en/latest/
.. _tox: https://testrun.org/tox/
