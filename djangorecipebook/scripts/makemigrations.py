"""
Calls the management script with the 'makemigrations' command
"""

import sys

from .manage import main as manage_main


def main(settings, *args, **kwargs):

    # we empty sys.argv so that command line params can be intercepted
    # by the make_*_migrations functions above
    sys_argv = sys.argv[1:]
    sys.argv = sys.argv[:1]

    manage_main(settings, 'makemigrations', *(list(args) + sys_argv))

    return 0
