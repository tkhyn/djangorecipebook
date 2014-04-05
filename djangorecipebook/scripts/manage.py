"""
Recipe generating a management script
"""

import os
import sys


def main(settings_module):
    # called on script execution
    from django.core import management
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
    management.execute_from_command_line(sys.argv)
