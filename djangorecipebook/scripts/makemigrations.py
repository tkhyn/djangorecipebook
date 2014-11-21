"""
Calls the management script with the 'makemigrations' command
"""

from .manage import manage_main


def main(settings_module, *args):
    manage_main(settings_module, 'makemigrations', *args)
