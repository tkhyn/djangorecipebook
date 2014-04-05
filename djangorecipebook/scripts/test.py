"""
Recipe generating a test script
"""

import os


def main(settings_file, *apps):
    from django.core import management
    argv = ['test', 'test'] + list(apps)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_file)
    management.execute_from_command_line(argv)
