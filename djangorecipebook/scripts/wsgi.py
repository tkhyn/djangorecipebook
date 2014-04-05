"""
Recipe generating a wsgi script
"""

# largely derived from R van Laar's djangorecipe

import os
import sys
import logging


def main(settings_file, logfile=None, level=logging.INFO):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_file)

    if logfile:
        # setup logging
        class StdStrLogger(object):
            def __init__(self, logger, level):
                self.logger = logger
                self.log_level = level

            def write(self, data):
                for line in data.rstrip().splitlines():
                    self.logger.log(self.log_level, line.rstrip())

        logging.basicConfig(
           level=level,
           format='%(asctime)s:%(levelname)s:%(message)s',
           datefmt='%Y%m%d %H:%M:%S',
           filename=logfile,
           filemode='a'
        )

        sys.stdout = StdStrLogger(logging.getLogger('stdout'), logging.INFO)
        sys.stderr = StdStrLogger(logging.getLogger('stdout'), logging.ERROR)

    # Run WSGI handler for the application
    from django.core.wsgi import get_wsgi_application
    return get_wsgi_application()
